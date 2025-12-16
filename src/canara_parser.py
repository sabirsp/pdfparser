import re
import pdfplumber
from datetime import datetime
from .models import Transaction

class CanaraTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        transactions = []
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    txs = self._extract_from_text(text)
                    transactions.extend(txs)
        
        return transactions
    
    def _extract_from_text(self, text):
        transactions = []
        lines = text.split('\n')
        prev_balance = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match date pattern at start
            date_match = re.match(r'^(\d{2}-\d{2}-\d{4})', line)
            if date_match:
                date_str = date_match.group(1)
                
                # Look back for description before date
                description_lines = []
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d{2}-\d{2}-\d{4}', prev_line) and 'Chq:' not in prev_line and 'Opening Balance' not in prev_line:
                        description_lines.append(prev_line)
                        # Check one more line back
                        if i > 1:
                            prev_prev = lines[i-2].strip()
                            if prev_prev and not re.match(r'^\d{2}-\d{2}-\d{4}', prev_prev) and 'Chq:' not in prev_prev:
                                description_lines.insert(0, prev_prev)
                
                # Parse amounts from the date line
                amounts = re.findall(r'([\d,]+\.\d{2})', line)
                
                if len(amounts) >= 2:
                    description = ' '.join(description_lines).strip()
                    date_obj = self._parse_date(date_str)
                    
                    if date_obj:
                        # Last amount is always balance
                        balance = self._parse_amount(amounts[-1])
                        amount = self._parse_amount(amounts[-2])
                        
                        # Use balance comparison to determine debit/credit
                        debit = 0.0
                        credit = 0.0
                        
                        if prev_balance is not None:
                            if balance > prev_balance:
                                credit = amount
                            else:
                                debit = amount
                        else:
                            # First transaction - check if balance increased
                            credit = amount
                        
                        prev_balance = balance
                        
                        transactions.append(Transaction(
                            date=date_obj,
                            description=description,
                            debit=debit,
                            credit=credit,
                            balance=balance,
                            bank_name='Canara Bank'
                        ))
                
                i += 1
            else:
                # Check for opening balance
                if 'Opening Balance' in line:
                    amounts = re.findall(r'([\d,]+\.\d{2})', line)
                    if amounts:
                        prev_balance = self._parse_amount(amounts[0])
                i += 1
        
        return transactions
    
    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
        except:
            return None
    
    def _parse_amount(self, amount_str):
        if not amount_str:
            return 0.0
        try:
            return float(amount_str.replace(',', ''))
        except:
            return 0.0
