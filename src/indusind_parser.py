import re
import pdfplumber
from datetime import datetime
from .models import Transaction

class IndusIndTransactionParser:
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
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Match date pattern: DD Mon YYYY
            date_match = re.match(r'^(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})', line)
            if date_match:
                date_str = date_match.group(1)
                
                # Extract amounts and reference from the same line
                amounts = re.findall(r'(\d+\.\d{2})', line)
                ref_match = re.search(r'(S\d+)', line)
                ref = ref_match.group(1) if ref_match else ''
                
                # Extract description (between date and reference)
                desc_start = len(date_str)
                desc_end = line.find(ref) if ref else line.rfind(' ')
                description = line[desc_start:desc_end].strip()
                
                # Check next line for continuation
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not re.match(r'^\d{1,2}\s+[A-Za-z]{3}\s+\d{4}', next_line):
                        description += ' ' + next_line
                        i += 1
                
                if len(amounts) >= 3:
                    date_obj = self._parse_date(date_str)
                    if date_obj:
                        withdrawal = float(amounts[0])
                        deposit = float(amounts[1])
                        balance = float(amounts[2])
                        
                        transactions.append(Transaction(
                            date=date_obj,
                            description=f"{description} | Ref: {ref}",
                            debit=withdrawal,
                            credit=deposit,
                            balance=balance,
                            bank_name='IndusInd Bank'
                        ))
            
            i += 1
        
        return transactions
    
    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%d %b %Y').strftime('%Y-%m-%d')
        except:
            return None
