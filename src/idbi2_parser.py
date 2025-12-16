import re
import pdfplumber
from .models import Transaction

class Idbi2Parser:
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
                    elif all_transactions and len(table) > 0:
                        transactions = self._extract_transactions_continuation(table)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'txn date' in header_str or ('date' in header_str and 'withdrawals' in header_str and 'deposits' in header_str)
    
    def _extract_transactions(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or not any(row) or len(row) < 8:
                continue
            
            date_cell = str(row[1]).replace('\n', ' ').strip() if len(row) > 1 and row[1] else ''
            particulars = str(row[3]).replace('\n', ' ').strip() if len(row) > 3 and row[3] else ''
            withdrawals_cell = str(row[5]).strip() if len(row) > 5 and row[5] else ''
            deposits_cell = str(row[6]).strip() if len(row) > 6 and row[6] else ''
            balance_cell = str(row[7]).strip() if len(row) > 7 and row[7] else ''
            
            dates = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', date_cell)
            if not dates:
                continue
            
            withdrawal = self._parse_amount(withdrawals_cell)
            deposit = self._parse_amount(deposits_cell)
            balance = self._parse_amount(balance_cell)
            
            transactions.append(Transaction(
                date=self._convert_date(dates[0]),
                description=particulars,
                debit=withdrawal,
                credit=deposit,
                balance=balance,
                bank_name='IDBI'
            ))
        
        return transactions
    
    def _extract_transactions_continuation(self, table):
        transactions = []
        
        for row in table:
            if not row or not any(row) or len(row) < 8:
                continue
            
            date_cell = str(row[1]).replace('\n', ' ').strip() if len(row) > 1 and row[1] else ''
            particulars = str(row[3]).replace('\n', ' ').strip() if len(row) > 3 and row[3] else ''
            withdrawals_cell = str(row[5]).strip() if len(row) > 5 and row[5] else ''
            deposits_cell = str(row[6]).strip() if len(row) > 6 and row[6] else ''
            balance_cell = str(row[7]).strip() if len(row) > 7 and row[7] else ''
            
            dates = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', date_cell)
            if not dates:
                continue
            
            withdrawal = self._parse_amount(withdrawals_cell)
            deposit = self._parse_amount(deposits_cell)
            balance = self._parse_amount(balance_cell)
            
            transactions.append(Transaction(
                date=self._convert_date(dates[0]),
                description=particulars,
                debit=withdrawal,
                credit=deposit,
                balance=balance,
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
        if '/' in date_str:
            parts = date_str.split('/')
        else:
            parts = date_str.split('-')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
