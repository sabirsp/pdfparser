#!/usr/bin/env python3
import sys
from src.yes_parser import YesTransactionParser

def test_yes_parser():
    # Replace with your actual PDF path
    pdf_path = "your_yes_bank_statement.pdf"
    
    parser = YesTransactionParser()
    transactions = parser.parse_transactions(pdf_path)
    
    print(f"\nFINAL RESULT: Found {len(transactions)} transactions")
    for i, tx in enumerate(transactions):
        print(f"{i+1}. {tx.date} | {tx.description[:50]}... | D:{tx.debit} C:{tx.credit} B:{tx.balance}")

if __name__ == "__main__":
    test_yes_parser()