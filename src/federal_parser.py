# src/federal_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class FederalTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Federal Bank")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                
                for table in tables:
                    if table and self._is_transaction_table(table):
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total Federal Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 1:
            return False
        
        first_row = table[0]
        if not first_row or len(first_row) < 10:
            return False
        
        # Check if first row is header
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        if any('date' in cell or 'particulars' in cell for cell in clean_first):
            return True
        
        # Check if first row is transaction data (date pattern)
        if re.match(r'\d{2}-[A-Z]{3}-\d{4}', str(first_row[0]).strip()):
            return True
        
        return False
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        # Check if first row is header
        first_row = table[0]
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        is_header = any('date' in cell or 'particulars' in cell for cell in clean_first)
        
        start_idx = 1 if is_header else 0
        
        for row in table[start_idx:]:
            if not row or not any(row):
                continue
            
            transaction = self._parse_table_row(row)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_table_row(self, row):
        try:
            while len(row) < 10:
                row.append('')
            
            cells = [str(cell).strip() if cell else '' for cell in row]
            
            date_str = cells[0]
            value_date = cells[1]
            particulars = cells[2].replace('\n', ' ')
            tran_type = cells[3]
            tran_id = cells[4]
            cheque_details = cells[5]
            withdrawals_str = cells[6]
            deposits_str = cells[7]
            balance_str = cells[8]
            dr_cr = cells[9]
            
            # Skip opening balance row
            if 'Opening Balance' in particulars:
                return None
            
            # Parse date (format: "02-APR-2024")
            date = self._parse_date(date_str)
            if not date:
                return None
            
            # Parse amounts
            withdrawals = self._parse_amount(withdrawals_str)
            deposits = self._parse_amount(deposits_str)
            balance = self._parse_amount(balance_str)
            
            if balance is None or balance == 0:
                return None
            
            description = f"{particulars} | Type: {tran_type} | ID: {tran_id}" if tran_id else particulars
            
            return Transaction(
                date=date,
                description=description,
                debit=withdrawals,
                credit=deposits,
                balance=balance,
                bank_name='FEDERAL'
            )
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Parse "02-APR-2024" format
            dt = datetime.strptime(date_str, '%d-%b-%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str or str(amount_str).strip() in ['', '-']:
            return 0.0
        
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0
