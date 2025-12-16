import re
import pdfplumber
from .models import Transaction

class Idbi1Parser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    if self._is_transaction_table(table):
                        transactions = self._extract_transactions(table)
                        all_transactions.extend(transactions)
                    elif all_transactions:
                        transactions = self._extract_transactions_continuation(table)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'date' in header_str and 'withdrawals' in header_str and 'deposits' in header_str
    
    def _extract_transactions(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or not any(row) or len(row) < 6:
                continue
            
            date_cell = str(row[0]).strip() if row[0] else ''
            particulars = str(row[1]).strip() if row[1] else ''
            withdrawals_cell = str(row[3]).strip() if row[3] else ''
            deposits_cell = str(row[4]).strip() if row[4] else ''
            balance_cell = str(row[5]).strip() if row[5] else ''
            
            dates = re.findall(r'\d{2}-\d{2}-\d{4}', date_cell)
            if not dates:
                continue
            
            if len(dates) > 1:
                date_parts = date_cell.split('\n')
                desc_parts = particulars.split('\n')
                withdrawal_parts = withdrawals_cell.split('\n') if '\n' in withdrawals_cell else [withdrawals_cell] * len(dates)
                deposit_parts = deposits_cell.split('\n') if '\n' in deposits_cell else [deposits_cell] * len(dates)
                balance_parts = balance_cell.split('\n') if '\n' in balance_cell else [balance_cell] * len(dates)
                
                for i in range(len(dates)):
                    transactions.append(Transaction(
                        date=self._convert_date(dates[i]),
                        description=desc_parts[i].strip() if i < len(desc_parts) else '',
                        debit=self._parse_amount(withdrawal_parts[i] if i < len(withdrawal_parts) else ''),
                        credit=self._parse_amount(deposit_parts[i] if i < len(deposit_parts) else ''),
                        balance=self._parse_amount(balance_parts[i] if i < len(balance_parts) else ''),
                        bank_name='IDBI'
                    ))
            else:
                transactions.append(Transaction(
                    date=self._convert_date(dates[0]),
                    description=particulars,
                    debit=self._parse_amount(withdrawals_cell),
                    credit=self._parse_amount(deposits_cell),
                    balance=self._parse_amount(balance_cell),
                    bank_name='IDBI'
                ))
        
        return transactions
    
    def _extract_transactions_continuation(self, table):
        transactions = []
        
        for row in table:
            if not row or not any(row) or len(row) < 6:
                continue
            
            date_cell = str(row[0]).strip() if row[0] else ''
            particulars = str(row[1]).strip() if row[1] else ''
            withdrawals_cell = str(row[3]).strip() if row[3] else ''
            deposits_cell = str(row[4]).strip() if row[4] else ''
            balance_cell = str(row[5]).strip() if row[5] else ''
            
            dates = re.findall(r'\d{2}-\d{2}-\d{4}', date_cell)
            if not dates:
                continue
            
            if len(dates) > 1:
                date_parts = date_cell.split('\n')
                desc_parts = particulars.split('\n')
                withdrawal_parts = withdrawals_cell.split('\n') if '\n' in withdrawals_cell else [withdrawals_cell] * len(dates)
                deposit_parts = deposits_cell.split('\n') if '\n' in deposits_cell else [deposits_cell] * len(dates)
                balance_parts = balance_cell.split('\n') if '\n' in balance_cell else [balance_cell] * len(dates)
                
                for i in range(len(dates)):
                    transactions.append(Transaction(
                        date=self._convert_date(dates[i]),
                        description=desc_parts[i].strip() if i < len(desc_parts) else '',
                        debit=self._parse_amount(withdrawal_parts[i] if i < len(withdrawal_parts) else ''),
                        credit=self._parse_amount(deposit_parts[i] if i < len(deposit_parts) else ''),
                        balance=self._parse_amount(balance_parts[i] if i < len(balance_parts) else ''),
                        bank_name='IDBI'
                    ))
            else:
                transactions.append(Transaction(
                    date=self._convert_date(dates[0]),
                    description=particulars,
                    debit=self._parse_amount(withdrawals_cell),
                    credit=self._parse_amount(deposits_cell),
                    balance=self._parse_amount(balance_cell),
                    bank_name='IDBI'
                ))
        
        return transactions
    
    def _parse_amount(self, value):
        if not value:
            return 0.0
        s = str(value).replace(',', '').replace('Cr', '').replace('Dr', '').strip()
        try:
            return float(re.sub(r'[^\d.]', '', s))
        except:
            return 0.0
    
    def _convert_date(self, date_str):
        parts = date_str.split('-')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
