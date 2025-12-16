import re
import pdfplumber
from datetime import datetime
from .models import Transaction

class KotakTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        txs = self._extract_from_table(table)
                        transactions.extend(txs)
        
        return transactions
    
    def _extract_from_table(self, table):
        transactions = []
        if not table or len(table) < 2:
            return transactions
        
        # Find header row
        header_idx = -1
        for i, row in enumerate(table):
            if row and any('Narration' in str(cell) for cell in row if cell):
                header_idx = i
                break
        
        if header_idx == -1:
            return transactions
        
        # Process data rows
        for row in table[header_idx + 1:]:
            if not row or len(row) < 6:
                continue
            
            date = str(row[0]).strip() if row[0] else ''
            narration = str(row[2]).replace('\n', ' ').strip() if row[2] else ''
            ref = str(row[3]).strip() if row[3] else ''
            withdrawal = str(row[4]).strip() if row[4] else ''
            deposit = str(row[5]).strip() if row[5] else ''
            balance = str(row[6]).strip() if row[6] else ''
            
            if not date or 'OPENING' in narration.upper():
                continue
            
            date_obj = self._parse_date(date)
            if not date_obj:
                continue
            
            debit = self._parse_amount(withdrawal)
            credit = self._parse_amount(deposit)
            balance_val = self._parse_amount(balance)
            
            transactions.append(Transaction(
                date=date_obj,
                description=f"{narration} | Ref: {ref}",
                debit=debit,
                credit=credit,
                balance=balance_val,
                bank_name='Kotak Mahindra Bank'
            ))
        
        return transactions
    
    def _parse_date(self, date_str):
        formats = ['%d-%b-%y', '%d-%b-%Y', '%d/%m/%Y', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        return None
    
    def _parse_amount(self, amount_str):
        if not amount_str:
            return 0.0
        s = str(amount_str).replace(',', '').replace('(Cr)', '').replace('(Dr)', '').strip()
        try:
            return float(re.sub(r'[^0-9.]', '', s))
        except:
            return 0.0
