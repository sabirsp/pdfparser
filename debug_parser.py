#!/usr/bin/env python3
import sys
from src.bank_parser import IndianBankStatementParser

def debug_parse(pdf_path):
    print(f"Debugging parser for: {pdf_path}")
    
    parser = IndianBankStatementParser()
    
    # Extract text first
    text = parser.pdf_processor.extract_text(pdf_path)
    print(f"Extracted text length: {len(text)} characters")
    print("First 500 characters:")
    print(text[:500])
    print("\n" + "="*50 + "\n")
    
    # Identify bank
    bank_name = parser.bank_identifier.identify_bank(text)
    print(f"Identified bank: {bank_name}")
    
    # Parse transactions
    transactions = parser.transaction_parser.parse_transactions(text, bank_name)
    print(f"Found {len(transactions)} transactions")
    
    if transactions:
        print("\nFirst few transactions:")
        for i, tx in enumerate(transactions[:3]):
            print(f"{i+1}. {tx.date} | {tx.description[:50]} | DR: {tx.debit} | CR: {tx.credit} | Bal: {tx.balance}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_parser.py <pdf_path>")
        sys.exit(1)
    
    debug_parse(sys.argv[1])