import pdfplumber

pdf_path = 'IDBI_99128926.PDF'
password = '99128926'

with pdfplumber.open(pdf_path, password=password) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for page_num, page in enumerate(pdf.pages[:3]):
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
        
        text = page.extract_text()
        print(f"\n--- Raw Text (first 1000 chars) ---")
        print(text[:1000] if text else "No text")
