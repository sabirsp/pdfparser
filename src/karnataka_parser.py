import re
import pdfplumber
from datetime import datetime
from .models import Transaction

class KarnatakaTransactionParser:
    def extract_transactions(self, pdf_path, password=None):
        transactions = []
        prev_balance = None
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    if 'Opening Balance' in line:
                        match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', line)
                        if match:
                            prev_balance = float(match.group(1).replace(',', ''))
                        continue
                    
                    tx = self._parse_transaction(line, prev_balance)
                    if tx:
                        transactions.append(tx)
                        prev_balance = tx.balance
        
        return transactions
    
    def _parse_transaction(self, line, prev_balance):
        # Match pattern: DD-MM-YYYY Description Amount Balance
        pattern = r'^(\d{2}-\d{2}-\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(\d{1,3}(?:,\d{3})*(?:\.\d{1,2}))$'
        
        match = re.match(pattern, line.strip())
        if not match:
            return None
        
        date_str, description, amount, balance = match.groups()
        
        amount_val = float(amount.replace(',', ''))
        balance_val = float(balance.replace(',', ''))
        
        # Determine debit/credit based on balance change
        debit = 0.0
        credit = 0.0
        
        if prev_balance is not None:
            if balance_val > prev_balance:
                credit = amount_val
            else:
                debit = amount_val
        else:
            credit = amount_val
        
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        
        return Transaction(
            date=date_obj.strftime('%Y-%m-%d'),
            description=description.strip(),
            debit=debit,
            credit=credit,
            balance=balance_val,
            bank_name='Karnataka Bank'
        )
