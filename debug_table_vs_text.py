#!/usr/bin/env python3
import pdfplumber

def debug_table_vs_text():
    pdf_path = "Statement-079561900004248-07-30-2025-17-06-53 (1).pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]  # First page
        
        print("=== TABLE EXTRACTION ===")
        tables = page.extract_tables()
        if tables and len(tables) > 1:
            table = tables[1]
            for i, row in enumerate(table):
                print(f"Row {i}: {row}")
        
        print("\n=== TEXT EXTRACTION ===")
        text = page.extract_text()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if '2025-' in line:
                print(f"Line {i}: {line}")

if __name__ == "__main__":
    debug_table_vs_text()