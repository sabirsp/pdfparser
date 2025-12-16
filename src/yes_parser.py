# src/yes_parser.py
import re
import pdfplumber
from .models import Transaction

class YesTransactionParser:
    def __init__(self):
        self.expected_headers = [
            'Transaction Date', 'Value Date', 'Description', 'Reference Number', 
            'Withdrawals', 'Deposits', 'Running Balance'
        ]
    
    def parse_transactions(self, pdf_path):
        all_transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Yes Bank")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                print(f"Found {len(tables)} tables on page {page_num + 1}")
                
                for table_idx, table in enumerate(tables):
                    print(f"\n--- Table {table_idx + 1} Structure ---")
                    if table:
                        print(f"Table size: {len(table)} rows x {len(table[0]) if table else 0} cols")
                        for i, row in enumerate(table[:3]):  # Show first 3 rows
                            print(f"Row {i}: {row}")
                    
                    if table and self._is_transaction_table(table):
                        print(f"Found transaction table on page {page_num + 1}, table {table_idx + 1}")
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from this table")
                    else:
                        print(f"Table {table_idx + 1} not recognized as transaction table")
        
        print(f"Total Yes Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header_row = table[0]
        if not header_row:
            return False
        
        clean_headers = [str(cell).strip().lower() if cell else '' for cell in header_row]
        print(f"Headers found: {clean_headers}")
        
        key_headers = ['transaction date', 'value date', 'description', 'reference number', 'withdrawals', 'deposits', 'running balance']
        matches = 0
        
        for key_header in key_headers:
            for cell in clean_headers:
                if key_header in cell:
                    matches += 1
                    break
        
        print(f"Header matches: {matches}/7")
        
        return matches >= 3
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        for row_idx, row in enumerate(table[1:], 1):
            if not row or not any(row):
                continue
            
            transaction = self._parse_table_row(row, row_idx)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_table_row(self, row, row_idx):
        try:
            print(f"Raw row {row_idx}: {row}")
            
            while len(row) < 7:
                row.append('')
            
            # Handle word-wrapped/line-broken cell values
            cells = [str(cell).replace('\n', ' ').replace('\r', ' ').strip() if cell else '' for cell in row]
            print(f"Cleaned cells: {cells}")
            
            transaction_date = cells[0]
            value_date = cells[1]
            description = cells[2]
            reference_number = cells[3]
            withdrawals_str = cells[4]
            deposits_str = cells[5]
            running_balance_str = cells[6]
            
            print(f"Date: {transaction_date}, W: {withdrawals_str}, D: {deposits_str}, Bal: {running_balance_str}")
            
            if not re.match(r'\d{4}-\d{2}-\d{2}', transaction_date):
                print(f"Date validation failed for: {transaction_date}")
                return None
            
            withdrawals = self._parse_amount(withdrawals_str)
            deposits = self._parse_amount(deposits_str)
            running_balance = self._parse_amount(running_balance_str)
            
            print(f"Parsed amounts - W: {withdrawals}, D: {deposits}, Bal: {running_balance}")
            
            if running_balance is None:
                return None
            
            return Transaction(
                date=transaction_date,
                description=f"{description} | Ref: {reference_number}" if reference_number else description,
                debit=withdrawals if withdrawals else 0,
                credit=deposits if deposits else 0,
                balance=running_balance,
                bank_name='YES'
            )
            
        except Exception as e:
            print(f"Error parsing Yes Bank row {row_idx}: {row}, Error: {e}")
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str or str(amount_str).strip() == '' or str(amount_str).strip() == '-' or str(amount_str).strip().lower() == '(blank)':
            return 0.0
        
        try:
            # Handle word-wrapped/line-broken values and various formats
            clean_str = str(amount_str).replace('\n', '').replace('\r', '').replace(' ', '')
            # Remove commas and keep only digits and decimal point
            clean_amount = ''.join(c for c in clean_str if c.isdigit() or c == '.')
            result = float(clean_amount) if clean_amount else 0.0
            print(f"Parsed '{amount_str}' -> {result}")
            return result
        except:
            print(f"Failed to parse amount: '{amount_str}'")
            return 0.0