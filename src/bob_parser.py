import re
import pdfplumber
from .models import Transaction

class BobTransactionParser:
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
        
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = str(table[0][0]).lower() if table[0] and table[0][0] else ''
        return 'date' in header and 'number' in header
    
    def _extract_transactions(self, table):
        transactions = []
        
        for row in table[1:]:
            if not row or not any(row) or len(row) < 5:
                continue
            
            first_cell = str(row[0]).strip() if row[0] else ''
            debit_cell = str(row[2]).strip() if len(row) > 2 and row[2] else ''
            credit_cell = str(row[3]).strip() if len(row) > 3 and row[3] else ''
            balance_cell = str(row[4]).strip() if len(row) > 4 and row[4] else ''
            
            date_match = re.search(r'(\d{2}-\d{2}-\d{4})', first_cell)
            if not date_match:
                continue
            
            # Remove serial number and all dates, keep description
            description = re.sub(r'^\d+\s+', '', first_cell)  # Remove leading serial number
            description = re.sub(r'\d{2}-\d{2}-\d{4}', '', description)  # Remove all dates
            description = re.sub(r'\n\d+\s+', ' ', description)  # Remove serial numbers after newlines
            description = description.replace('\n', ' ').strip()
            
            transactions.append(Transaction(
                date=self._convert_date(date_match.group(1)),
                description=description,
                debit=self._parse_amount(debit_cell),
                credit=self._parse_amount(credit_cell),
                balance=self._parse_amount(balance_cell),
                bank_name='Bank of Baroda'
            ))
        
        return transactions
    
    def _parse_amount(self, value):
        if not value or value == '-':
            return 0.0
        s = str(value).replace(',', '').strip()
        try:
            return float(re.sub(r'[^\d.]', '', s))
        except:
            return 0.0
    
    def _convert_date(self, date_str):
        parts = date_str.split('-')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
