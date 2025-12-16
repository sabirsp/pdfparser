#!/usr/bin/env python3
import pdfplumber

def debug_iob_pdf():
    pdf_path = "Indian_Overseas_bank_51087192.pdf"
    password = "51087192"
    
    print(f"Analyzing IOB PDF: {pdf_path}")
    print(f"Using password: {password}\n")
    
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"✅ PDF opened successfully!")
            print(f"Total pages: {len(pdf.pages)}\n")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"=== PAGE {page_num + 1} ===")
                
                # Extract text
                text = page.extract_text()
                if text:
                    print(f"Text length: {len(text)}")
                    print("First 500 characters:")
                    print(text[:500])
                    print("\n" + "-"*50)
                
                # Extract tables
                tables = page.extract_tables()
                print(f"Found {len(tables)} tables\n")
                
                for table_idx, table in enumerate(tables):
                    print(f"--- Table {table_idx + 1} ---")
                    if table:
                        print(f"Size: {len(table)} rows x {len(table[0]) if table else 0} cols")
                        
                        # Show first 5 rows
                        for i, row in enumerate(table[:5]):
                            print(f"Row {i}: {row}")
                        
                        if len(table) > 5:
                            print(f"... and {len(table) - 5} more rows")
                    print()
                
                # Look for transaction patterns in text
                print("Lines with dates (Mar, Apr, etc.):")
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if any(month in line for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                        print(f"Line {i}: {line}")
                
                print("\n" + "="*50 + "\n")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_iob_pdf()