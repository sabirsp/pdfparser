import pdfplumber
import re

pdf_path = 'IDBI_Bank_2.pdf'
password = ''

with pdfplumber.open(pdf_path, password=password) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    table = tables[1]  # Second table
    header = [str(cell).lower() if cell else '' for cell in table[0]]
    has_sno = 's.no' in ' '.join(header)
    
    print(f"Has S.No: {has_sno}")
    print(f"\nProcessing first data row:")
    row = table[1]
    print(f"Row: {row}")
    
    date_cell = str(row[1]).replace('\n', ' ').strip() if len(row) > 1 and row[1] else ''
    print(f"Date cell: '{date_cell}'")
    
    dates = re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', date_cell)
    print(f"Dates found: {dates}")
    
    particulars = str(row[3]).replace('\n', ' ').strip() if len(row) > 3 and row[3] else ''
    print(f"Description: '{particulars}'")
    
    withdrawals_cell = str(row[5]).strip() if len(row) > 5 and row[5] else ''
    deposits_cell = str(row[6]).strip() if len(row) > 6 and row[6] else ''
    balance_cell = str(row[7]).strip() if len(row) > 7 and row[7] else ''
    
    print(f"Withdrawals: '{withdrawals_cell}'")
    print(f"Deposits: '{deposits_cell}'")
    print(f"Balance: '{balance_cell}'")
