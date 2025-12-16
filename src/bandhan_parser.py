# src/bandhan_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class BandhanTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Bandhan Bank")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                
                for table in tables:
                    if table and self._is_transaction_table(table):
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total Bandhan Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 1:
            return False
        
        first_row = table[0]
        if not first_row:
            return False
        
        # Check if first row is header
        clean_headers = [str(cell).strip().lower().replace('\n', ' ') if cell else '' for cell in first_row]
        
        # Support both formats:
        # New format: TRANS DATE, VALUE DATE, CHEQUE/INSTRUMENT, DESCRIPTION, DEBITS, CREDITS, BALANCE (7 cols)
        # Old format: Transaction Date, Value Date, Description, Amount, DR/CR, Balance (6 cols)
        new_format_headers = ['trans date', 'value date', 'description', 'debits', 'credits', 'balance']
        old_format_headers = ['transaction date', 'value date', 'description', 'amount', 'dr / cr', 'balance']
        
        new_matches = sum(1 for key in new_format_headers if any(key in cell for cell in clean_headers))
        old_matches = sum(1 for key in old_format_headers if any(key in cell for cell in clean_headers))
        
        if new_matches >= 3 or old_matches >= 3:
            return True
        
        return False
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        # Check if first row is header or data
        first_row = table[0]
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        is_header = any('transaction date' in cell or 'value date' in cell or 'trans date' in cell for cell in clean_first)
        
        # Detect format based on number of columns
        num_cols = len(first_row) if first_row else 0
        is_new_format = num_cols >= 7  # New format has 7 columns
        
        start_idx = 1 if is_header else 0
        
        for row in table[start_idx:]:
            if not row or not any(row):
                continue
            
            transaction = self._parse_table_row(row, is_new_format)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_table_row(self, row, is_new_format=True):
        try:
            cells = [str(cell).strip().replace('\n', ' ') if cell else '' for cell in row]
            
            if is_new_format:
                # New format: TRANS DATE, VALUE DATE, CHEQUE/INSTRUMENT, DESCRIPTION, DEBITS, CREDITS, BALANCE (7 cols)
                while len(cells) < 7:
                    cells.append('')
                
                transaction_date = cells[0]
                cheque_instrument = cells[2]
                description = cells[3]
                debits_str = cells[4]
                credits_str = cells[5]
                balance_str = cells[6]
                
                date = self._parse_date(transaction_date)
                if not date:
                    return None
                
                debits = self._parse_amount(debits_str)
                credits = self._parse_amount(credits_str)
                balance = self._parse_amount(balance_str)
                
                full_desc = f"{description} | Ref: {cheque_instrument}" if cheque_instrument else description
            else:
                # Old format: Transaction Date, Value Date, Description, Amount, DR/CR, Balance (6 cols)
                while len(cells) < 6:
                    cells.append('')
                
                transaction_date = cells[0]
                description = cells[2]
                amount_str = cells[3]
                dr_cr = cells[4]
                balance_str = cells[5]
                
                date = self._parse_date(transaction_date)
                if not date:
                    return None
                
                amount = self._parse_amount(amount_str)
                balance = self._parse_amount(balance_str)
                
                debits = amount if dr_cr.strip().upper() == 'DR' else 0
                credits = amount if dr_cr.strip().upper() == 'CR' else 0
                full_desc = description
            
            if balance is None:
                return None
            
            return Transaction(
                date=date,
                description=full_desc,
                debit=debits,
                credit=credits,
                balance=balance,
                bank_name='BANDHAN'
            )
            
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Remove extra spaces and clean up (handle "01-APR- 2018" -> "01-APR-2018")
            clean_date = date_str.strip().replace('- ', '-')
            
            # Try "01-APR-2018" format
            try:
                dt = datetime.strptime(clean_date, '%d-%b-%Y')
                return dt.strftime('%Y-%m-%d')
            except:
                pass
            
            # Try "June30, 2025" format (old format)
            try:
                dt = datetime.strptime(clean_date, '%B%d, %Y')
                return dt.strftime('%Y-%m-%d')
            except:
                pass
            
            return None
        except:
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str or str(amount_str).strip() in ['', '-']:
            return 0.0
        
        try:
            # Remove commas and parse
            clean_str = str(amount_str).replace(',', '').strip()
            return float(clean_str) if clean_str else 0.0
        except:
            return 0.0
