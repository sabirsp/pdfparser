import pdfplumber
import re
from src.models import Transaction

pdf_path = 'IDBI_Bank_2.pdf'
password = ''

all_transactions = []

with pdfplumber.open(pdf_path, password=password) as pdf:
    print(f"Pages: {len(pdf.pages)}")
    
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        print(f"Page {page_num+1}: {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            if not table or len(table) < 2:
                print(f"  Table {table_idx+1}: Skipped (too small)")
                continue
            
            header = [str(cell).lower() if cell else '' for cell in table[0]]
            is_txn_table = 'date' in ' '.join(header) and 'withdrawals' in ' '.join(header) and 'deposits' in ' '.join(header)
            
            print(f"  Table {table_idx+1}: Is transaction table: {is_txn_table}")
            
            if is_txn_table:
                has_sno = 's.no' in ' '.join(header)
                print(f"    Has S.No: {has_sno}")
                
                for row_idx, row in enumerate(table[1:], 1):
                    if not row or not any(row):
                        continue
                    
                    if has_sno:
                        date_cell = str(row[1]).replace('\n', ' ').strip() if len(row) > 1 and row[1] else ''
                        particulars = str(row[3]).replace('\n', ' ').strip() if len(row) > 3 and row[3] else ''
                        withdrawals_cell = str(row[5]).strip() if len(row) > 5 and row[5] else ''
                        deposits_cell = str(row[6]).strip() if len(row) > 6 and row[6] else ''
                        balance_cell = str(row[7]).strip() if len(row) > 7 and row[7] else ''
                    else:
                        date_cell = str(row[0]).replace('\n', '|').strip() if row[0] else ''
                        particulars = str(row[1]).replace('\n', '|').strip() if row[1] else ''
                        withdrawals_cell = str(row[3]).replace('\n', '|').strip() if len(row) > 3 and row[3] else ''
                        deposits_cell = str(row[4]).replace('\n', '|').strip() if len(row) > 4 and row[4] else ''
                        balance_cell = str(row[5]).replace('\n', '|').strip() if len(row) > 5 and row[5] else ''
                    
                    dates = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', date_cell)
                    if not dates:
                        print(f"    Row {row_idx}: No date found in '{date_cell}'")
                        continue
                    
                    all_transactions.append({
                        'date': dates[0],
                        'description': particulars,
                        'debit': withdrawals_cell,
                        'credit': deposits_cell,
                        'balance': balance_cell
                    })

print(f"\nTotal transactions: {len(all_transactions)}")
for t in all_transactions[:3]:
    print(f"{t['date']} | {t['description'][:40]} | D:{t['debit']} C:{t['credit']}")
