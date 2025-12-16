#!/usr/bin/env python3
import pdfplumber
import sys
import os

def debug_pdf_structure():
    # Look for PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]  # Use first PDF found
    print(f"Analyzing PDF: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages):
            print(f"\n=== PAGE {page_num + 1} ===")
            
            # Extract text first
            text = page.extract_text()
            if text:
                print("Text sample (first 500 chars):")
                print(text[:500])
                print("\n" + "-"*50)
            
            # Extract tables
            tables = page.extract_tables()
            print(f"Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                print(f"\n--- Table {table_idx + 1} ---")
                if table:
                    print(f"Size: {len(table)} rows x {len(table[0]) if table else 0} cols")
                    
                    # Show all rows for small tables, first 5 for large ones
                    rows_to_show = min(len(table), 5)
                    for i in range(rows_to_show):
                        print(f"Row {i}: {table[i]}")
                    
                    if len(table) > 5:
                        print(f"... and {len(table) - 5} more rows")
                else:
                    print("Empty table")

if __name__ == "__main__":
    debug_pdf_structure()