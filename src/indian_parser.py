# src/indian_parser.py
import re
import pdfplumber
from .models import Transaction
from datetime import datetime

class IndianBankTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        all_transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Processing {len(pdf.pages)} pages for Indian Bank")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"Processing page {page_num + 1}")
                text = page.extract_text()
                transactions = self._extract_from_text(text)
                all_transactions.extend(transactions)
                print(f"Extracted {len(transactions)} transactions from page {page_num + 1}")
        
        print(f"Total Indian Bank transactions extracted: {len(all_transactions)}")
        return all_transactions
    
    def _extract_from_text(self, text):
        transactions = []
        lines = text.split('\n')
        
        # Get brought forward balance for this page
        page_start_balance = None
        for line in lines:
            if 'Brought Forward' in line:
                balance_match = re.search(r'([\d,]+\.\d{2})(cr|Cr|dr|Dr)', line, re.IGNORECASE)
                if balance_match:
                    page_start_balance = self._parse_amount(balance_match.group(1))
                break
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for date pattern at start of line
            date_match = re.match(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})', line)
            if date_match:
                # Collect multi-line transaction
                tx_lines = [line]
                i += 1
                
                # Continue until we hit next date, brought/carried forward, or closing balance
                while i < len(lines):
                    next_line = lines[i].strip()
                    if re.match(r'\d{2}/\d{2}/\d{2}', next_line) or 'Brought Forward' in next_line or 'Carried Forward' in next_line or 'CLOSING BALANCE' in next_line:
                        break
                    tx_lines.append(next_line)
                    i += 1
                
                tx = self._parse_transaction(tx_lines, page_start_balance)
                if tx:
                    transactions.append(tx)
                    page_start_balance = tx.balance
            else:
                i += 1
        
        return transactions
    
    def _parse_transaction(self, lines, prev_balance):
        try:
            full_text = ' '.join(lines)
            
            # Extract dates from first line
            first_line = lines[0]
            date_match = re.match(r'(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})', first_line)
            if not date_match:
                return None
            
            post_date = date_match.group(1)
            date = self._parse_date(post_date)
            if not date:
                return None
            
            # Extract balance (ends with Cr, Dr, or standalone at end)
            balance_match = re.search(r'([\d,]+\.\d{2})(Cr|Dr)', full_text)
            if not balance_match:
                # For zero balance or balance without Cr/Dr, find last amount in last line
                last_line = lines[-1].strip()
                amounts_in_last = re.findall(r'([\d,]+\.\d{2})', last_line)
                if amounts_in_last:
                    balance = self._parse_amount(amounts_in_last[-1])
                else:
                    return None
            else:
                balance = self._parse_amount(balance_match.group(1))
            
            # Determine debit/credit by comparing balances
            debit = 0
            credit = 0
            
            if prev_balance is not None:
                diff = balance - prev_balance
                if diff < 0:
                    # Balance decreased = debit
                    debit = abs(diff)
                elif diff > 0:
                    # Balance increased = credit
                    credit = diff
            else:
                # Fallback: extract amount from text
                remaining_text = full_text[:balance_match.start()]
                remaining_amounts = re.findall(r'([\d,]+\.\d{2})', remaining_text)
                if remaining_amounts:
                    amount = self._parse_amount(remaining_amounts[-1])
                    if 'TRANSFER TO' in full_text or 'DEBIT' in full_text:
                        debit = amount
                    else:
                        credit = amount
            
            # Extract description (remove dates and amounts)
            description = re.sub(r'\d{2}/\d{2}/\d{2}', '', full_text)
            description = re.sub(r'[\d,]+\.\d{2}(Cr|Dr)?', '', description)
            description = ' '.join(description.split())
            
            return Transaction(
                date=date,
                description=description,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name='INDIAN'
            )
        except Exception as e:
            return None
    
    def _parse_date(self, date_str):
        try:
            # Parse "01/01/23" format
            dt = datetime.strptime(date_str, '%d/%m/%y')
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0
