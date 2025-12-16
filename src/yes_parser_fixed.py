# src/yes_parser_fixed.py
import re
import pdfplumber
from .models import Transaction

class YesTransactionParserFixed:
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
                
                # Try multiple table extraction strategies
                tables = self._extract_tables_multiple_strategies(page)
                
                for table_idx, table in enumerate(tables):
                    if table and self._is_transaction_table(table):
                        print(f"Found transaction table on page {page_num + 1}, table {table_idx + 1}")
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from this table")
        
        print(f"Total Yes Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _extract_tables_multiple_strategies(self, page):
        """Try different table extraction strategies"""
        strategies = [
            {},  # Default
            {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            {"vertical_strategy": "text", "horizontal_strategy": "text"},
            {"snap_tolerance": 3, "join_tolerance": 3}
        ]
        
        for i, settings in enumerate(strategies):
            try:
                tables = page.extract_tables(table_settings=settings)
                print(f"Strategy {i+1}: Found {len(tables)} tables")
                if tables:
                    return tables
            except:
                continue
        
        return []
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        # Check first row for headers
        header_row = table[0]
        if not header_row:
            return False
        
        # Join all header cells and check for key terms
        header_text = ' '.join(str(cell).lower() if cell else '' for cell in header_row)
        print(f"Header text: {header_text}")
        
        key_terms = ['transaction', 'date', 'description', 'withdrawals', 'deposits', 'balance']
        matches = sum(1 for term in key_terms if term in header_text)
        
        print(f"Header matches: {matches}/{len(key_terms)}")
        return matches >= 4
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        print(f"Table structure: {len(table)} rows x {len(table[0]) if table else 0} cols")
        
        # Show table structure for debugging
        for i, row in enumerate(table[:3]):
            print(f"Row {i}: {row}")
        
        # Skip header row and process data rows
        for row_idx, row in enumerate(table[1:], 1):
            if not row or not any(row):
                continue
            
            transaction = self._parse_table_row_flexible(row, row_idx)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_table_row_flexible(self, row, row_idx):
        """Flexible row parsing that handles different column counts"""
        try:
            print(f"Raw row {row_idx}: {row}")
            
            # Clean cells
            cells = [str(cell).replace('\n', ' ').replace('\r', ' ').strip() if cell else '' for cell in row]
            print(f"Cleaned cells ({len(cells)}): {cells}")
            
            # Handle different column scenarios
            if len(cells) >= 8:
                # 8-column format with empty column 3
                return self._parse_8_column_row(cells, row_idx)
            elif len(cells) >= 7:
                # Standard 7-column format
                return self._parse_7_column_row(cells, row_idx)
            elif len(cells) >= 6:
                # 6-column format (maybe reference number missing)
                return self._parse_6_column_row(cells, row_idx)
            else:
                print(f"Row {row_idx}: Not enough columns ({len(cells)})")
                return None
                
        except Exception as e:
            print(f"Error parsing row {row_idx}: {e}")
            return None
    
    def _parse_7_column_row(self, cells, row_idx):
        """Parse standard 7-column row"""
        transaction_date = cells[0]
        value_date = cells[1]
        description = cells[2]
        reference_number = cells[3]
        withdrawals_str = cells[4]
        deposits_str = cells[5]
        running_balance_str = cells[6]
        
        return self._create_transaction(transaction_date, description, reference_number, 
                                      withdrawals_str, deposits_str, running_balance_str, row_idx)
    
    def _parse_8_column_row(self, cells, row_idx):
        """Parse 8-column row with empty column 3"""
        transaction_date = cells[0]
        value_date = cells[1]
        description = cells[2]
        # cells[3] is empty - skip it
        reference_number = cells[4]
        withdrawals_str = cells[5]
        deposits_str = cells[6]
        running_balance_str = cells[7]
        
        return self._create_transaction(transaction_date, description, reference_number,
                                      withdrawals_str, deposits_str, running_balance_str, row_idx)
    
    def _parse_6_column_row(self, cells, row_idx):
        """Parse 6-column row (assuming reference number is missing)"""
        transaction_date = cells[0]
        value_date = cells[1]
        description = cells[2]
        reference_number = ""  # Missing
        withdrawals_str = cells[3]
        deposits_str = cells[4]
        running_balance_str = cells[5]
        
        return self._create_transaction(transaction_date, description, reference_number,
                                      withdrawals_str, deposits_str, running_balance_str, row_idx)
    
    def _create_transaction(self, transaction_date, description, reference_number,
                          withdrawals_str, deposits_str, running_balance_str, row_idx):
        """Create transaction from parsed fields"""
        
        print(f"Fields - Date: {transaction_date}, Desc: {description[:30]}..., Ref: {reference_number}")
        print(f"Amounts - W: '{withdrawals_str}', D: '{deposits_str}', Bal: '{running_balance_str}'")
        
        # Validate date
        if not re.match(r'\d{4}-\d{2}-\d{2}', transaction_date):
            print(f"Date validation failed: {transaction_date}")
            return None
        
        # Parse amounts
        withdrawals = self._parse_amount(withdrawals_str)
        deposits = self._parse_amount(deposits_str)
        running_balance = self._parse_amount(running_balance_str)
        
        print(f"Parsed amounts - W: {withdrawals}, D: {deposits}, Bal: {running_balance}")
        
        if running_balance is None:
            print("Invalid running balance")
            return None
        
        return Transaction(
            date=transaction_date,
            description=f"{description} | Ref: {reference_number}" if reference_number else description,
            debit=withdrawals if withdrawals else 0,
            credit=deposits if deposits else 0,
            balance=running_balance,
            bank_name='YES'
        )
    
    def _parse_amount(self, amount_str):
        if not amount_str or str(amount_str).strip() == '' or str(amount_str).strip() == '-' or str(amount_str).strip().lower() == '(blank)':
            return 0.0
        
        try:
            # Handle various formats
            clean_str = str(amount_str).replace('\n', '').replace('\r', '').replace(' ', '')
            # Remove commas and keep only digits and decimal point
            clean_amount = ''.join(c for c in clean_str if c.isdigit() or c == '.')
            result = float(clean_amount) if clean_amount else 0.0
            print(f"Amount '{amount_str}' -> {result}")
            return result
        except:
            print(f"Failed to parse amount: '{amount_str}'")
            return 0.0