#!/usr/bin/env python3
import pdfplumber

def test_different_extraction_strategies():
    pdf_path = "Statement-079561900004248-07-30-2025-17-06-53 (1).pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]  # Test on first page
        
        print("=== STRATEGY 1: Default ===")
        tables1 = page.extract_tables()
        if tables1 and len(tables1) > 1:
            table = tables1[1]  # Second table
            for i, row in enumerate(table):
                print(f"Row {i}: {row}")
        
        print("\n=== STRATEGY 2: Text-based ===")
        tables2 = page.extract_tables(table_settings={
            "vertical_strategy": "text",
            "horizontal_strategy": "text"
        })
        if tables2 and len(tables2) > 1:
            table = tables2[1]
            for i, row in enumerate(table):
                print(f"Row {i}: {row}")
        
        print("\n=== STRATEGY 3: Lines-based ===")
        tables3 = page.extract_tables(table_settings={
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines"
        })
        if tables3 and len(tables3) > 1:
            table = tables3[1]
            for i, row in enumerate(table):
                print(f"Row {i}: {row}")
        
        print("\n=== STRATEGY 4: Explicit settings ===")
        tables4 = page.extract_tables(table_settings={
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit",
            "explicit_vertical_lines": [],
            "explicit_horizontal_lines": [],
            "snap_tolerance": 3,
            "join_tolerance": 3
        })
        if tables4 and len(tables4) > 1:
            table = tables4[1]
            for i, row in enumerate(table):
                print(f"Row {i}: {row}")
        
        print("\n=== RAW TEXT ANALYSIS ===")
        text = page.extract_text()
        lines = text.split('\n')
        print("Lines containing dates:")
        for i, line in enumerate(lines):
            if '2025-' in line:
                print(f"Line {i}: {line}")

if __name__ == "__main__":
    test_different_extraction_strategies()