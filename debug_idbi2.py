import pdfplumber

pdf_path = 'IDBI_Bank_2.pdf'
password = ''

with pdfplumber.open(pdf_path, password=password) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for page_num, page in enumerate(pdf.pages[:2]):
        print(f"\n{'='*60}")
        print(f"PAGE {page_num + 1}")
        print(f"{'='*60}")
        
        tables = page.extract_tables()
        print(f"\nTables found: {len(tables)}")
        
        for idx, table in enumerate(tables):
            print(f"\n--- Table {idx + 1} ---")
            if table:
                print(f"Rows: {len(table)}, Cols: {len(table[0]) if table else 0}")
                for i, row in enumerate(table[:5]):
                    print(f"Row {i}: {row}")
