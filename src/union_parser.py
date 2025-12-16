# src/union_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class UnionTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Union Bank")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                tables = page.extract_tables()
                
                for table in tables:
                    if table and self._is_transaction_table(table):
                        transactions = self._extract_transactions_from_table(table)
                        all_transactions.extend(transactions)
                        print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total Union Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 1:
            return False
        
        first_row = table[0]
        if not first_row or len(first_row) < 6:
            return False
        
        # Check if first row is header
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        if any('s.no' in cell or 'date' in cell for cell in clean_first):
            return True
        
        # Check if first row is transaction data (S.No starts with digit)
        if re.match(r'\d+', str(first_row[0]).strip()):
            return True
        
        return False
    
    def _extract_transactions_from_table(self, table):
        transactions = []
        
        # Check if first row is header
        first_row = table[0]
        clean_first = [str(cell).strip().lower() if cell else '' for cell in first_row]
        is_header = any('s.no' in cell or 'transaction id' in cell for cell in clean_first)
        
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
            while len(row) < 6:
                row.append('')
            
            cells = [str(cell).strip() if cell else '' for cell in row]
            
            sno = cells[0]
            date_str = cells[1]
            transaction_id = cells[2]
            remarks = cells[3].replace('\n', ' ')
            amount_str = cells[4]
            balance_str = cells[5]
            
            # Validate S.No
            if not re.match(r'\d+', sno):
                return None
            
            # Parse date (format: "27/03/2025")
            date = self._parse_date(date_str)
            if not date:
                return None
            
            # Parse amounts
            amount, is_debit = self._parse_amount(amount_str)
            balance = self._parse_balance(balance_str)
            
            if balance is None:
                return None
            
            debit = amount if is_debit else 0
            credit = amount if not is_debit else 0
            
            description = f"{remarks} | Txn ID: {transaction_id}" if transaction_id else remarks
            
            return Transaction(
                date=date,
                description=description,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name='UNION'
            )
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Parse "27/03/2025" format
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        try:
            # Extract amount and Dr/Cr indicator
            # Format: "50000.00 (Dr)" or "960.72 (Cr)"
            match = re.search(r'([\d,]+\.\d{2})\s*\((Dr|Cr)\)', amount_str)
            if match:
                amount = float(match.group(1).replace(',', ''))
                is_debit = match.group(2) == 'Dr'
                return amount, is_debit
            return 0.0, True
        except:
            return 0.0, True
    
    def _parse_balance(self, balance_str):
        try:
            # Extract balance (format: "650640.45 (Cr)")
            match = re.search(r'([\d,]+\.\d{2})', balance_str)
            if match:
                return float(match.group(1).replace(',', ''))
            return None
        except:
            return None
