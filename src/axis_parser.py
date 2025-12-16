# src/axis_parser.py
import re
import pdfplumber
from .models import Transaction

class AxisTransactionParser:
    def __init__(self):
        self.expected_headers = [
            'S.No', 'Transaction Date', 'Value Date', 'Particulars', 
            'Amount (INR)', 'Debit/Credit', 'Balance(INR)', 'Cheque Number', 'Branch Name(SOL)'
        ]
    
    def parse_transactions(self, pdf_path):
        all_transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                
                for table_idx, table in enumerate(tables):
                    if table and self._is_transaction_table(table):
                        print(f"Found transaction table on page {page_num + 1}, table {table_idx + 1}")
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from this table")
        
        print(f"Total transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 1:
            return False
        
        header_row = table[0]
        if not header_row:
            return False
        
        # Clean and normalize headers
        clean_headers = [str(cell).strip().lower().replace('\n', ' ') if cell else '' for cell in header_row]
        
        # Check if it's a header row
        format1_headers = ['s.no', 'transaction date', 'particulars', 'amount', 'debit/credit', 'balance']
        format2_headers = ['tran date', 'chq no', 'particulars', 'debit', 'credit', 'balance']
        
        format1_matches = sum(1 for key in format1_headers if any(key in cell for cell in clean_headers))
        format2_matches = sum(1 for key in format2_headers if any(key in cell for cell in clean_headers))
        
        if format1_matches >= 4 or format2_matches >= 4:
            return True
        
        # If no header match, check if it's a continuation page (data rows without header)
        # Format 2: 7 columns with date pattern in first column
        # Format 1: 9 columns with numeric S.No in first column
        if len(header_row) == 7:
            # Check if first cell looks like a date (DD-MM-YYYY)
            first_cell = str(header_row[0]).strip()
            if re.match(r'\d{2}-\d{2}-\d{4}', first_cell):
                return True
        elif len(header_row) == 9:
            # Check if first cell is numeric (S.No)
            first_cell = str(header_row[0]).strip()
            try:
                int(first_cell)
                return True
            except:
                pass
        
        return False
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        if not table or len(table) < 1:
            return transactions
        
        # Detect format based on headers or first row structure
        header_row = table[0]
        clean_headers = [str(cell).strip().lower().replace('\n', ' ') if cell else '' for cell in header_row]
        
        # Check if first row is header
        has_header = any('tran date' in cell or 'transaction date' in cell for cell in clean_headers)
        is_format2 = any('tran date' in cell for cell in clean_headers) and any('chq no' in cell for cell in clean_headers)
        
        # If no header, detect format by checking first data row
        if not has_header and len(table) > 0:
            first_row = table[0]
            # Format 2 has 7 columns, Format 1 has 9 columns
            is_format2 = len(first_row) == 7
        
        # Start from row 1 if header exists, else row 0
        start_idx = 1 if has_header else 0
        
        for row_idx, row in enumerate(table[start_idx:], start_idx):
            if not row or not any(row):  # Skip empty rows
                continue
            
            transaction = self._parse_table_row(row, row_idx, is_format2)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_table_row(self, row, row_idx, is_format2=False):
        try:
            # Clean cell values (handle multi-line cells)
            cells = [str(cell).strip().replace('\n', ' ') if cell else '' for cell in row]
            
            if is_format2:
                # Format 2: Tran Date, Chq No, Particulars, Debit, Credit, Balance, Init. Br (7 cols)
                while len(cells) < 7:
                    cells.append('')
                
                tran_date = cells[0]
                chq_no = cells[1]
                particulars = cells[2]
                debit_str = cells[3]
                credit_str = cells[4]
                balance_str = cells[5]
                
                # Validate date format (DD-MM-YYYY)
                if not re.match(r'\d{2}-\d{2}-\d{4}', tran_date):
                    return None
                
                debit = self._parse_amount(debit_str)
                credit = self._parse_amount(credit_str)
                balance = self._parse_amount(balance_str)
                
                if balance is None:
                    return None
                
                # Convert date format DD-MM-YYYY to DD/MM/YYYY
                date = tran_date.replace('-', '/')
                desc = f"{particulars} | Ref: {chq_no}" if chq_no else particulars
            else:
                # Format 1: S.No, Transaction Date, Value Date, Particulars, Amount, Debit/Credit, Balance (9 cols)
                while len(cells) < 9:
                    cells.append('')
                
                sno = cells[0]
                transaction_date = cells[1]
                particulars = cells[3]
                amount_str = cells[4]
                debit_credit = cells[5]
                balance_str = cells[6]
                
                # Validate S.No (should be numeric)
                try:
                    int(sno)
                except:
                    return None
                
                # Validate date format (DD/MM/YYYY)
                if not re.match(r'\d{2}/\d{2}/\d{4}', transaction_date):
                    return None
                
                amount = self._parse_amount(amount_str)
                balance = self._parse_amount(balance_str)
                
                if amount is None or balance is None:
                    return None
                
                debit = amount if debit_credit.upper() == 'DR' else 0
                credit = amount if debit_credit.upper() == 'CR' else 0
                date = transaction_date
                desc = particulars
            
            return Transaction(
                date=date,
                description=desc,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name='AXIS'
            )
            
        except Exception as e:
            print(f"Error parsing row {row_idx}: {row}, Error: {e}")
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str:
            return 0.0
        
        try:
            # Remove commas and convert to float
            clean_amount = amount_str.replace(',', '').replace('₹', '').strip()
            return float(clean_amount)
        except:
            return None