# src/iob_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class IOBTransactionParser:
    def __init__(self):
        self.expected_headers = [
            'Date', 'Particulars', 'Ref No.', 'Transaction Type', 
            'Debit', 'Credit', 'Balance'
        ]
    
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for IOB")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                
                for table in tables:
                    if table and self._is_transaction_table(table):
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total IOB transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 1:
            return False
        
        first_row = table[0]
        if not first_row or len(first_row) < 7:
            return False
        
        # Check if first row is a header
        clean_headers = [str(cell).strip().lower() if cell else '' for cell in first_row]
        key_headers = ['date', 'particulars', 'ref no', 'transaction type', 'debit', 'credit', 'balance']
        header_matches = sum(1 for key in key_headers if any(key in cell for cell in clean_headers))
        
        if header_matches >= 4:
            return True
        
        # Check if first row is transaction data (continuation page without header)
        date_str = str(first_row[0]).strip()
        if re.search(r'\d{2}-[A-Za-z]{3}-\d{2}', date_str):
            return True
        
        return False
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        # Check if first row is header or data
        first_row = table[0]
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        is_header = any('date' in cell or 'particulars' in cell for cell in clean_first)
        
        # Start from row 1 if header, row 0 if data
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
            while len(row) < 7:
                row.append('')
            
            cells = [str(cell).strip() if cell else '' for cell in row]
            
            date_str = cells[0].replace('\n', ' ')
            particulars = cells[1].replace('\n', ' ')
            ref_no = cells[2].replace('\n', ' ')
            transaction_type = cells[3].replace('\n', ' ')
            debit_str = cells[4]
            credit_str = cells[5]
            balance_str = cells[6]
            
            # Parse date (format: "06-Jun-24 (06-Jun-24)" or "06-Jun-24")
            date_match = re.search(r'(\d{2}-[A-Za-z]{3}-\d{2})', date_str)
            if not date_match:
                return None
            
            date = self._parse_date(date_match.group(1))
            if not date:
                return None
            
            debit = self._parse_amount(debit_str)
            credit = self._parse_amount(credit_str)
            balance = self._parse_amount(balance_str)
            
            if balance is None:
                return None
            
            description = f"{particulars} | {transaction_type}" if transaction_type and transaction_type != '-' else particulars
            if ref_no and ref_no != '-':
                description = f"{description} | Ref: {ref_no}"
            
            return Transaction(
                date=date,
                description=description,
                debit=debit if debit else 0,
                credit=credit if credit else 0,
                balance=balance,
                bank_name='IOB'
            )
            
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Parse "06-Jun-24" format
            dt = datetime.strptime(date_str, '%d-%b-%y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str or str(amount_str).strip() in ['', '-']:
            return 0.0
        
        try:
            # Remove commas from Indian number format (1,27,448.20)
            clean_str = str(amount_str).replace(',', '').strip()
            return float(clean_str) if clean_str else 0.0
        except:
            return 0.0
