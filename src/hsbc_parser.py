# src/hsbc_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class HSBCTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for HSBC")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                text = page.extract_text()
                transactions = self._extract_from_text(text)
                all_transactions.extend(transactions)
                print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total HSBC transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _extract_from_text(self, text):
        transactions = []
        lines = text.split('\n')
        
        last_date = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for date pattern
            date_match = re.match(r'(\d{1,2}[A-Za-z]{3}\d{4})', line)
            if date_match:
                last_date = date_match.group(1)
                remaining = line[len(last_date):].strip()
                if remaining:
                    tx = self._parse_transaction(last_date, remaining, lines, i)
                    if tx:
                        transactions.append(tx)
                i += 1
            elif last_date and line and re.match(r'UPI\d+', line):
                # New transaction starts with UPI reference
                tx = self._parse_transaction(last_date, line, lines, i)
                if tx:
                    transactions.append(tx)
                i += 1
            else:
                i += 1
        
        return transactions
    
    def _parse_transaction(self, date_str, first_line, all_lines, start_idx):
        try:
            # Collect multi-line transaction details
            details = [first_line]
            i = start_idx + 1
            
            # Continue collecting lines until we hit amount pattern or next date
            while i < len(all_lines):
                line = all_lines[i].strip()
                if not line or re.match(r'\d{1,2}[A-Za-z]{3}\d{4}', line) or line.startswith('CLOSING'):
                    break
                # Check if line contains amount pattern (ends with number)
                if re.search(r'[\d,]+\.\d{2}$', line):
                    details.append(line)
                    break
                details.append(line)
                i += 1
            
            full_text = ' '.join(details)
            
            # Extract amounts from the last line
            amounts = re.findall(r'([\d,]+\.\d{2})', full_text)
            if len(amounts) < 1:
                return None
            
            # Parse date
            date = self._parse_date(date_str)
            if not date:
                return None
            
            # Determine debit/credit/balance
            if len(amounts) == 1:
                # Only balance (like BALANCE BROUGHT FORWARD)
                balance = self._parse_amount(amounts[0])
                debit = 0
                credit = 0
            elif len(amounts) == 2:
                # withdrawal/deposit + balance
                amount = self._parse_amount(amounts[0])
                balance = self._parse_amount(amounts[1])
                # Determine if debit or credit based on description
                if 'UPI' in full_text or 'PAY' in full_text:
                    debit = amount
                    credit = 0
                else:
                    debit = 0
                    credit = amount
            else:
                # Multiple amounts - take last as balance
                balance = self._parse_amount(amounts[-1])
                amount = self._parse_amount(amounts[-2])
                debit = amount
                credit = 0
            
            # Clean description
            description = re.sub(r'[\d,]+\.\d{2}', '', full_text).strip()
            
            return Transaction(
                date=date,
                description=description,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name='HSBC'
            )
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Parse "26Jun2025" format
            dt = datetime.strptime(date_str, '%d%b%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0
