import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class JKBankTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                if tables and len(tables) > 0:
                    for table in tables:
                        if self._is_transaction_table(table):
                            transactions = self._extract_from_table(table)
                            all_transactions.extend(transactions)
                else:
                    text = page.extract_text()
                    transactions = self._extract_from_text(text)
                    all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'date' in header_str and 'particulars' in header_str and ('withdrawals' in header_str or 'deposits' in header_str)
    
    def _extract_from_table(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or len(row) < 6:
                continue
            
            date = str(row[0]).strip() if row[0] else ''
            particulars = str(row[1]).strip() if row[1] else ''
            withdrawals = str(row[3]).strip() if row[3] else ''
            deposits = str(row[4]).strip() if row[4] else ''
            balance = str(row[5]).strip() if row[5] else ''
            
            if not date or not re.match(r'\d{2}-\d{2}-\d{4}', date):
                continue
            
            debit_val = self._parse_amount(withdrawals)
            credit_val = self._parse_amount(deposits)
            balance_val = self._parse_amount(balance)
            
            particulars_clean = particulars.replace('\n', ' ').strip()
            
            transactions.append(Transaction(
                date=self._parse_date(date),
                description=particulars_clean,
                debit=debit_val,
                credit=credit_val,
                balance=balance_val,
                bank_name='JK'
            ))
        
        return transactions
    
    def _extract_from_text(self, text):
        transactions = []
        lines = text.split('\n')
        prev_balance = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            date_match = re.match(r'(\d{2}-\d{2}-\d{4})', line)
            if date_match:
                tx_lines = [line]
                i += 1
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    if re.match(r'\d{2}-\d{2}-\d{4}', next_line) or next_line.startswith('---') or next_line.startswith('B/F') or next_line.startswith('C/F') or next_line.startswith('Page Total'):
                        break
                    tx_lines.append(next_line)
                    i += 1
                
                tx = self._parse_transaction_new_format(tx_lines, prev_balance)
                if tx:
                    transactions.append(tx)
                    prev_balance = tx.balance
            else:
                i += 1
        
        return transactions
    
    def _parse_transaction_new_format(self, lines, prev_balance):
        try:
            full_text = ' '.join(lines)
            
            first_line = lines[0]
            date_match = re.match(r'(\d{2}-\d{2}-\d{4})', first_line)
            if not date_match:
                return None
            
            date_str = date_match.group(1)
            date = self._parse_date(date_str)
            if not date:
                return None
            
            balance_match = re.search(r'([\d,]+\.\d{2})(Cr|Dr)', full_text)
            if not balance_match:
                return None
            
            balance = self._parse_amount(balance_match.group(1))
            
            # Extract all amounts from the text
            amounts = re.findall(r'([\d,]+\.\d{2})', full_text)
            
            # Find withdrawal and deposit amounts
            debit = 0
            credit = 0
            
            if len(amounts) >= 2:
                balance_idx = amounts.index(balance_match.group(1))
                before_balance = amounts[:balance_idx]
                
                if len(before_balance) == 1:
                    # Only one amount before balance - use balance change to determine type
                    amt = self._parse_amount(before_balance[0])
                    
                    if prev_balance is not None:
                        if balance > prev_balance:
                            credit = amt
                        elif balance < prev_balance:
                            debit = amt
                    else:
                        # First transaction - assume it's a credit if balance is positive
                        credit = amt
                        
                elif len(before_balance) >= 2:
                    # Two amounts before balance - first is withdrawal, second is deposit
                    debit = self._parse_amount(before_balance[0])
                    credit = self._parse_amount(before_balance[1])
            
            # Extract description
            description = re.sub(r'\d{2}-\d{2}-\d{4}', '', full_text)
            description = re.sub(r'[\d,]+\.\d{2}(Cr|Dr)?', '', description)
            description = ' '.join(description.split())
            
            return Transaction(
                date=date,
                description=description,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name='JK'
            )
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, '%d-%m-%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str or amount_str == '':
            return 0.0
        s = str(amount_str).replace(',', '').replace('Cr', '').replace('Dr', '').strip()
        try:
            return float(re.sub(r'[^\d.]', '', s))
        except:
            return 0.0
