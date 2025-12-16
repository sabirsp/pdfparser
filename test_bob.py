import pdfplumber

pdf_path = 'bob_9593597852.pdf'
password = '9593597852'

with pdfplumber.open(pdf_path, password=password) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for page_num, page in enumerate(pdf.pages[:2]):
        print(f"=== PAGE {page_num + 1} ===")
        tables = page.extract_tables()
        print(f"Tables found: {len(tables)}\n")
        
        for table_num, table in enumerate(tables):
            if table:
                print(f"--- Table {table_num + 1} ---")
                print(f"Rows: {len(table)}")
                for i, row in enumerate(table[:5]):
                    print(f"Row {i}: {row}")
                print()
