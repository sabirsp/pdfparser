import re
import pdfplumber
from .models import Transaction

class CbiTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    if self._is_transaction_table(table):
                        transactions = self._extract_transactions(table)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower().replace('\n', ' ') if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'post date' in header_str and 'debit' in header_str and 'credit' in header_str
    
    def _extract_transactions(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or len(row) < 8:
                continue
            
            post_date = str(row[0]).strip() if row[0] else ''
            description = str(row[4]).strip() if row[4] else ''
            debit = str(row[5]).strip() if row[5] else ''
            credit = str(row[6]).strip() if row[6] else ''
            balance = str(row[7]).strip() if row[7] else ''
            
            if not post_date or not re.match(r'\d{2}/\d{2}/\d{4}', post_date):
                continue
            
            debit_val = self._parse_amount(debit)
            credit_val = self._parse_amount(credit)
            balance_val = self._parse_amount(balance)
            
            description_clean = description.replace('\n', ' ').strip()
            
            transactions.append(Transaction(
                date=post_date,
                description=description_clean,
                debit=debit_val,
                credit=credit_val,
                balance=balance_val,
                bank_name='CBI'
            ))
        
        return transactions
    
    def _parse_amount(self, value):
        if not value or value == '':
            return 0.0
        s = str(value).replace(',', '').replace('CR', '').replace('DR', '').strip()
        try:
            return float(re.sub(r'[^\d.]', '', s))
        except:
            return 0.0
