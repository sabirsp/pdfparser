import re
import pdfplumber
from .models import Transaction

class HdfcTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    if self._is_transaction_table(table):
                        transactions = self._extract_transactions(table, all_transactions)
                        all_transactions.extend(transactions)
                    elif all_transactions and len(table) > 0:
                        transactions = self._extract_transactions_continuation(table, all_transactions)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'narration' in header_str and 'withdrawal' in header_str and 'deposit' in header_str
    
    def _extract_transactions(self, table, all_transactions):
        transactions = []
        
        for row in table[1:]:
            if not row or not any(row) or len(row) < 7:
                continue
            
            dates = [d for d in str(row[0]).strip().split('\n') if d]
            narrations_lines = str(row[1]).strip().split('\n') if row[1] else []
            withdrawals = [self._parse_amount(w) for w in str(row[4]).strip().split('\n') if w]
            deposits = [self._parse_amount(d) for d in str(row[5]).strip().split('\n') if d]
            balances = [self._parse_amount(b) for b in str(row[6]).strip().split('\n') if b]
            
            num_dates = len(dates)
            lines_per_txn = len(narrations_lines) // num_dates if num_dates > 0 else 0
            narrations = []
            
            for i in range(num_dates):
                start_idx = i * lines_per_txn
                end_idx = start_idx + lines_per_txn if i < num_dates - 1 else len(narrations_lines)
                narr = ' '.join(narrations_lines[start_idx:end_idx])
                narrations.append(narr)
            
            w_idx = 0
            d_idx = 0
            
            for i in range(num_dates):
                date = dates[i]
                narration = narrations[i] if i < len(narrations) else ''
                balance = balances[i] if i < len(balances) else 0
                
                if not re.match(r'\d{2}/\d{2}/\d{2}', date):
                    continue
                
                if i > 0:
                    prev_bal = balances[i-1]
                elif all_transactions or transactions:
                    prev_bal = (all_transactions[-1].balance if all_transactions and not transactions 
                               else transactions[-1].balance if transactions else 0)
                else:
                    prev_bal = 0
                
                if i == 0 and not all_transactions and not transactions:
                    if w_idx < len(withdrawals):
                        debit = withdrawals[w_idx]
                        credit = 0
                        w_idx += 1
                    elif d_idx < len(deposits):
                        debit = 0
                        credit = deposits[d_idx]
                        d_idx += 1
                    else:
                        debit = credit = 0
                elif balance < prev_bal:
                    debit = withdrawals[w_idx] if w_idx < len(withdrawals) else 0
                    credit = 0
                    w_idx += 1
                elif balance > prev_bal:
                    debit = 0
                    credit = deposits[d_idx] if d_idx < len(deposits) else 0
                    d_idx += 1
                else:
                    debit = credit = 0
                
                transactions.append(Transaction(
                    date=self._convert_date(date),
                    description=narration,
                    debit=debit,
                    credit=credit,
                    balance=balance,
                    bank_name='HDFC'
                ))
        
        return transactions
    
    def _extract_transactions_continuation(self, table, all_transactions):
        transactions = []
        
        for row in table:
            if not row or not any(row) or len(row) < 7:
                continue
            
            dates = [d for d in str(row[0]).strip().split('\n') if d]
            narrations_lines = str(row[1]).strip().split('\n') if row[1] else []
            withdrawals = [self._parse_amount(w) for w in str(row[4]).strip().split('\n') if w]
            deposits = [self._parse_amount(d) for d in str(row[5]).strip().split('\n') if d]
            balances = [self._parse_amount(b) for b in str(row[6]).strip().split('\n') if b]
            
            num_dates = len(dates)
            lines_per_txn = len(narrations_lines) // num_dates if num_dates > 0 else 0
            narrations = []
            
            for i in range(num_dates):
                start_idx = i * lines_per_txn
                end_idx = start_idx + lines_per_txn if i < num_dates - 1 else len(narrations_lines)
                narr = ' '.join(narrations_lines[start_idx:end_idx])
                narrations.append(narr)
            
            w_idx = 0
            d_idx = 0
            
            for i in range(num_dates):
                date = dates[i]
                narration = narrations[i] if i < len(narrations) else ''
                balance = balances[i] if i < len(balances) else 0
                
                if not re.match(r'\d{2}/\d{2}/\d{2}', date):
                    continue
                
                if i > 0:
                    prev_bal = balances[i-1]
                elif all_transactions or transactions:
                    prev_bal = (all_transactions[-1].balance if all_transactions and not transactions 
                               else transactions[-1].balance if transactions else 0)
                else:
                    prev_bal = 0
                
                if balance < prev_bal:
                    debit = withdrawals[w_idx] if w_idx < len(withdrawals) else 0
                    credit = 0
                    w_idx += 1
                elif balance > prev_bal:
                    debit = 0
                    credit = deposits[d_idx] if d_idx < len(deposits) else 0
                    d_idx += 1
                else:
                    debit = credit = 0
                
                transactions.append(Transaction(
                    date=self._convert_date(date),
                    description=narration,
                    debit=debit,
                    credit=credit,
                    balance=balance,
                    bank_name='HDFC'
                ))
        
        return transactions
    
    def _parse_amount(self, value):
        if not value or value == '':
            return 0.0
        s = str(value).replace(',', '').strip()
        try:
            return float(re.sub(r'[^\d.]', '', s))
        except:
            return 0.0
    
    def _convert_date(self, date_str):
        parts = date_str.split('/')
        day, month, year = parts[0], parts[1], parts[2]
        full_year = f"20{year}" if len(year) == 2 else year
        return f"{full_year}-{month}-{day}"
