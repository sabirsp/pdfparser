#!/usr/bin/env python3
from src.yes_parser_fixed import YesTransactionParserFixed

def test_fixed_parser():
    pdf_path = "Statement-079561900004248-07-30-2025-17-06-53 (1).pdf"
    
    parser = YesTransactionParserFixed()
    transactions = parser.parse_transactions(pdf_path)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total transactions found: {len(transactions)}")
    
    for i, tx in enumerate(transactions, 1):
        print(f"\n{i}. Date: {tx.date}")
        print(f"   Description: {tx.description}")
        print(f"   Debit: ₹{tx.debit:,.2f}")
        print(f"   Credit: ₹{tx.credit:,.2f}")
        print(f"   Balance: ₹{tx.balance:,.2f}")

if __name__ == "__main__":
    test_fixed_parser()