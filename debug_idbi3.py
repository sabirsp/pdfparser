import pdfplumber
import re

pdf_path = 'IDBI_Bank_2.pdf'
password = ''

with pdfplumber.open(pdf_path, password=password) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    for idx, table in enumerate(tables):
        if not table or len(table) < 2:
            print(f"Table {idx+1}: Too small")
            continue
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        print(f"\nTable {idx+1} headers: {header}")
        
        has_date = 'date' in ' '.join(header)
        has_withdrawals = 'withdrawals' in ' '.join(header) or 'dr' in ' '.join(header)
        has_deposits = 'deposits' in ' '.join(header) or 'cr' in ' '.join(header)
        
        print(f"Has date: {has_date}")
        print(f"Has withdrawals: {has_withdrawals}")
        print(f"Has deposits: {has_deposits}")
        print(f"Is transaction table: {has_date and has_withdrawals and has_deposits}")
