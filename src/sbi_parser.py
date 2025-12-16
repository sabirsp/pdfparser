import pdfplumber
import re
from datetime import datetime
from typing import List, Dict, Any
from src.models import Transaction

def parse_sbi_statement(pdf_path: str, password: str = None) -> Dict[str, Any]:
    transactions = []
    
    with pdfplumber.open(pdf_path, password=password) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                for row in table:
                    if not row or len(row) < 7:
                        continue
                    
                    # Skip header rows
                    if any(h in str(row[0]) for h in ['Txn', 'Date', 'Value']):
                        continue
                    
                    # Handle both 7-column and 8-column formats
                    if len(row) == 7:
                        # Format: Txn Date, Value Date, Description, Ref No./Cheque No., Debit, Credit, Balance
                        txn_date = row[0]
                        description = row[2]
                        ref_no = row[3]
                        debit = row[4]
                        credit = row[5]
                        balance = row[6]
                    else:
                        # Format: Txn Date, Value Date, Description, Ref No./Cheque No., Branch Code, Debit, Credit, Balance
                        txn_date = row[0]
                        description = row[2]
                        ref_no = row[3]
                        debit = row[5]
                        credit = row[6]
                        balance = row[7]
                    
                    # Skip empty rows
                    if not txn_date or not balance:
                        continue
                    
                    # Parse date - handle "1 Sep 2025" or "1 Sep2025"
                    date_str = txn_date.replace('\n', ' ').strip()
                    date_str = re.sub(r'\s+', ' ', date_str)
                    try:
                        parsed_date = datetime.strptime(date_str, '%d %b %Y')
                    except:
                        continue
                    
                    # Clean description
                    desc_clean = description.replace('\n', ' ').strip() if description else ''
                    ref_clean = ref_no.replace('\n', ' ').strip() if ref_no else ''
                    full_desc = f"{desc_clean} | Ref: {ref_clean}" if ref_clean else desc_clean
                    
                    # Parse amounts - handle Indian format "20,00,000.00"
                    def parse_amount(amt_str):
                        if not amt_str or amt_str.strip() == '':
                            return 0.0
                        cleaned = amt_str.replace('\n', '').replace(',', '').strip()
                        try:
                            return float(cleaned)
                        except:
                            return 0.0
                    
                    debit_amt = parse_amount(debit)
                    credit_amt = parse_amount(credit)
                    balance_amt = parse_amount(balance)
                    
                    transactions.append(Transaction(
                        date=parsed_date.date(),
                        description=full_desc,
                        debit=debit_amt,
                        credit=credit_amt,
                        balance=balance_amt,
                        bank_name='SBI'
                    ))
    
    return transactions
