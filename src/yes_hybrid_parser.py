# src/yes_hybrid_parser.py
import re
import pdfplumber
from .models import Transaction

class YesHybridParser:
    def __init__(self):
        pass
    
    def parse_transactions(self, pdf_path):
        all_transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        transactions = self._extract_from_table(table)
                        all_transactions.extend(transactions)
        
        return all_transactions
    
    def _extract_from_table(self, table):
        transactions = []
        if not table or len(table) < 2:
            return transactions
        
        header = table[0]
        if not self._is_transaction_table(header):
            return transactions
        
        for row in table[1:]:
            if not row or len(row) < 7:
                continue
            
            tx_date = str(row[0]).strip() if row[0] else ''
            description = str(row[3]).replace('\n', ' ').strip() if row[3] else ''
            reference = str(row[2]).replace('\n', '').strip() if row[2] else ''
            withdrawal = str(row[4]).strip() if row[4] else ''
            deposit = str(row[5]).strip() if row[5] else ''
            balance = str(row[6]).replace('\n', '').strip() if row[6] else ''
            
            if not tx_date:
                continue
            
            debit = self._parse_amount(withdrawal)
            credit = self._parse_amount(deposit)
            balance_val = self._parse_amount(balance)
            
            date_obj = self._parse_date(tx_date)
            if not date_obj:
                continue
            
            transactions.append(Transaction(
                date=date_obj,
                description=f"{description} | Ref: {reference}",
                debit=debit,
                credit=credit,
                balance=balance_val,
                bank_name='YES'
            ))
        
        return transactions
    
    def _is_transaction_table(self, header):
        header_str = ' '.join([str(h).lower() if h else '' for h in header])
        return 'transaction date' in header_str and 'withdrawals' in header_str and 'deposits' in header_str
    
    def _parse_date(self, date_str):
        from datetime import datetime
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%d-%b-%Y', '%d-%B-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        return None
    
    def _parse_amount(self, amount_str):
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0