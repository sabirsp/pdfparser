import re
import pdfplumber
from .models import Transaction

class PnbTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 1:
                        continue
                    
                    if self._is_transaction_table(table):
                        transactions = self._extract_transactions(table)
                        all_transactions.extend(transactions)
                    elif page_num > 0:
                        transactions = self._extract_transactions_continuation(table)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'date' in header_str and 'amount' in header_str and 'type' in header_str and 'balance' in header_str
    
    def _extract_transactions(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or len(row) < 6:
                continue
            
            date = str(row[0]).strip() if row[0] else ''
            amount = str(row[2]).strip() if row[2] else ''
            txn_type = str(row[3]).strip().upper() if row[3] else ''
            balance = str(row[4]).strip() if row[4] else ''
            remarks = str(row[5]).strip() if row[5] else ''
            
            if not date or not re.match(r'\d{2}/\d{2}/\d{4}', date):
                continue
            
            amount_val = self._parse_amount(amount)
            balance_val = self._parse_amount(balance)
            
            if txn_type == 'DR':
                debit = amount_val
                credit = 0.0
            elif txn_type == 'CR':
                debit = 0.0
                credit = amount_val
            else:
                debit = credit = 0.0
            
            remarks_clean = remarks.replace('\n', ' ').strip()
            
            transactions.append(Transaction(
                date=date,
                description=remarks_clean,
                debit=debit,
                credit=credit,
                balance=balance_val,
                bank_name='PNB'
            ))
        
        return transactions
    
    def _extract_transactions_continuation(self, table):
        transactions = []
        
        for row in table:
            if not row or len(row) < 6:
                continue
            
            date = str(row[0]).strip() if row[0] else ''
            amount = str(row[2]).strip() if row[2] else ''
            txn_type = str(row[3]).strip().upper() if row[3] else ''
            balance = str(row[4]).strip() if row[4] else ''
            remarks = str(row[5]).strip() if row[5] else ''
            
            if not date or not re.match(r'\d{2}/\d{2}/\d{4}', date):
                continue
            
            amount_val = self._parse_amount(amount)
            balance_val = self._parse_amount(balance)
            
            if txn_type == 'DR':
                debit = amount_val
                credit = 0.0
            elif txn_type == 'CR':
                debit = 0.0
                credit = amount_val
            else:
                debit = credit = 0.0
            
            remarks_clean = remarks.replace('\n', ' ').strip()
            
            transactions.append(Transaction(
                date=date,
                description=remarks_clean,
                debit=debit,
                credit=credit,
                balance=balance_val,
                bank_name='PNB'
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
