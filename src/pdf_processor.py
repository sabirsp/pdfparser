# src/pdf_processor.py
import pdfplumber
import pandas as pd

class PDFProcessor:
    def extract_text(self, pdf_path, password=None):
        """Extract raw text from PDF"""
        text = ""
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def extract_tables(self, pdf_path):
        """Extract tables from PDF"""
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.append(table)
        return tables

if __name__ == "__main__":
    # Usage
    processor = PDFProcessor()
    text = processor.extract_text("statement.pdf")
    print("Extracted Text:", text)