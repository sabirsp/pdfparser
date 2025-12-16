#!/usr/bin/env python3
import pdfplumber
import re

def analyze_raw_text():
    pdf_path = "Statement-079561900004248-07-30-2025-17-06-53 (1).pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n=== PAGE {page_num + 1} RAW TEXT ===")
            text = page.extract_text()
            
            # Split into lines and look for transaction patterns
            lines = text.split('\n')
            
            print("Lines with dates (2025-):")
            for i, line in enumerate(lines):
                if '2025-' in line:
                    print(f"Line {i}: '{line}'")
            
            print("\nLines with transaction keywords:")
            keywords = ['RTGS', 'UPI', 'IMPS', 'REVERSAL', 'Collection']
            for i, line in enumerate(lines):
                if any(keyword in line.upper() for keyword in keywords):
                    print(f"Line {i}: '{line}'")
            
            print("\nLines with reference numbers (YES/YBP/YESI):")
            for i, line in enumerate(lines):
                if re.search(r'YES[0-9A-Z]+', line):
                    print(f"Line {i}: '{line}'")
            
            # Look for amount patterns
            print("\nLines with amounts (comma-separated numbers):")
            for i, line in enumerate(lines):
                if re.search(r'\d{1,3}(?:,\d{3})+\.\d{2}', line):
                    print(f"Line {i}: '{line}'")

if __name__ == "__main__":
    analyze_raw_text()