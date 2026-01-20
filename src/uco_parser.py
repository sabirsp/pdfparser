import re
from datetime import datetime
from .models import Transaction

class UCOBankParser:
    def parse(self, text, pdf_path=None, password=None):
        transactions = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match: DD-Mon-YYYY followed by numbers (withdrawal/deposit and balance)
            # Format: 25-Nov-2025 5000 2044646 or 08-Oct-2025 350000 1849646
            match = re.match(r'^(\d{2}-[A-Za-z]{3}-\d{4})\s+(\d+(?:\.\d{1,2})?)\s+(\d+(?:\.\d{1,2})?)', line)
            
            if match:
                date_str = match.group(1)
                amount1 = float(match.group(2))
                amount2 = float(match.group(3))
                
                # amount1 is withdrawal or deposit, amount2 is balance
                withdrawal = amount1
                deposit = 0.0
                balance = amount2
                
                # Collect particulars from previous lines
                particulars = []
                j = i - 1
                while j >= 0 and j > i - 5:  # Look back max 5 lines
                    prev_line = lines[j].strip()
                    # Stop if we hit another date or empty line or header
                    if re.match(r'^\d{2}-[A-Za-z]{3}-\d{4}', prev_line) or not prev_line or 'Date' in prev_line:
                        break
                    particulars.insert(0, prev_line)
                    j -= 1
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, '%d-%b-%Y').date()
                except:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%B-%Y').date()
                    except:
                        i += 1
                        continue
                
                # Create transaction
                transaction = Transaction(
                    date=date_obj,
                    description=' '.join(particulars).strip(),
                    debit=withdrawal,
                    credit=deposit,
                    balance=balance,
                    bank_name='UCO'
                )
                transactions.append(transaction)
            
            i += 1
        
        return transactions
