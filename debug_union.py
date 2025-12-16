#!/usr/bin/env python3
import pdfplumber

pdf_path = "Union_Bank.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for page_idx in range(min(3, len(pdf.pages))):
        page = pdf.pages[page_idx]
        print(f"=== PAGE {page_idx + 1} ===")
        
        text = page.extract_text()
        if text:
            lines = text.split('\n')[:40]
            print("First 40 lines:")
            for i, line in enumerate(lines):
                print(f"{i}: {line}")
        
        tables = page.extract_tables()
        print(f"\nTables found: {len(tables)}")
        
        for table_idx, table in enumerate(tables):
            if table:
                print(f"\nTable {table_idx + 1}: {len(table)} rows x {len(table[0])} cols")
                for i in range(min(8, len(table))):
                    print(f"Row {i}: {table[i]}")
        print("\n" + "="*60 + "\n")
