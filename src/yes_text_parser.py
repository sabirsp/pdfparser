# src/yes_text_parser.py
import re
import pdfplumber
from .models import Transaction

class YesTextParser:
    def __init__(self):
        self.transaction_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+([A-Z0-9]+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})$'
        )
    
    def parse_transactions(self, pdf_path):
        all_transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Yes Bank (Text-based)")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                text = page.extract_text()
                
                transactions = self._extract_transactions_from_text(text, page_num + 1)
                all_transactions.extend(transactions)
                print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total Yes Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _extract_transactions_from_text(self, text, page_num):
        transactions = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for lines with date pattern at start
            if re.match(r'\d{4}-\d{2}-\d{2}', line):
                transaction = self._parse_transaction_line(line, page_num, line_num)
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    def _parse_transaction_line(self, line, page_num, line_num):
        try:
            print(f"Page {page_num}, Line {line_num}: {line}")
            
            # Split by spaces and reconstruct
            parts = line.split()
            if len(parts) < 6:
                return None
            
            # Extract components
            transaction_date = parts[0]
            value_date = parts[1]
            
            # Find amounts (last two parts should be amounts)
            amount1 = parts[-2]  # Second last
            amount2 = parts[-1]  # Last (balance)
            
            # Find reference number (before amounts, contains letters and numbers)
            ref_idx = -3
            while ref_idx >= -len(parts):
                if re.match(r'[A-Z0-9]+', parts[ref_idx]) and len(parts[ref_idx]) > 5:
                    break
                ref_idx -= 1
            
            if ref_idx < -len(parts):
                ref_idx = -3  # Default
            
            reference_number = parts[ref_idx]
            
            # Description is everything between value_date and reference_number
            desc_start = 2
            desc_end = len(parts) + ref_idx
            description = ' '.join(parts[desc_start:desc_end])
            
            # Parse amounts
            amount1_val = self._parse_amount(amount1)
            balance_val = self._parse_amount(amount2)
            
            # Determine if it's debit or credit based on description
            is_credit = any(keyword in description.upper() for keyword in ['CR', 'CREDIT', 'DEPOSIT'])
            
            debit = amount1_val if not is_credit else 0
            credit = amount1_val if is_credit else 0
            
            print(f"Parsed: Date={transaction_date}, Desc={description[:30]}..., Ref={reference_number}, Amount={amount1_val}, Balance={balance_val}")
            
            return Transaction(
                date=transaction_date,
                description=f"{description} | Ref: {reference_number}",
                debit=debit,
                credit=credit,
                balance=balance_val,
                bank_name='YES'
            )
            
        except Exception as e:
            print(f"Error parsing line: {line}, Error: {e}")
            return None
    
    def _parse_amount(self, amount_str):
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0