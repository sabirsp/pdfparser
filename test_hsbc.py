#!/usr/bin/env python3
from src.hsbc_parser import HSBCTransactionParser

pdf_path = "HSBC.pdf"
password = "100693425002"

parser = HSBCTransactionParser()
transactions = parser.parse_transactions(pdf_path, password=password)

print(f"\n{'='*60}")
print(f"Total Transactions: {len(transactions)}")
print(f"{'='*60}\n")

if transactions:
    print("All transactions:")
    for i, tx in enumerate(transactions, 1):
        print(f"\n{i}. Date: {tx.date}")
        print(f"   Description: {tx.description[:80]}...")
        print(f"   Debit: ₹{tx.debit:,.2f}")
        print(f"   Credit: ₹{tx.credit:,.2f}")
        print(f"   Balance: ₹{tx.balance:,.2f}")
else:
    print("No transactions found!")
