#!/usr/bin/env python3
from src.union_parser import UnionTransactionParser

pdf_path = "Union_Bank.pdf"

parser = UnionTransactionParser()
transactions = parser.parse_transactions(pdf_path)

print(f"\n{'='*60}")
print(f"Total Transactions: {len(transactions)}")
print(f"{'='*60}\n")

if transactions:
    print("First 5 transactions:")
    for i, tx in enumerate(transactions[:5], 1):
        print(f"\n{i}. Date: {tx.date}")
        print(f"   Description: {tx.description[:70]}...")
        print(f"   Debit: ₹{tx.debit:,.2f}")
        print(f"   Credit: ₹{tx.credit:,.2f}")
        print(f"   Balance: ₹{tx.balance:,.2f}")
    
    print(f"\n\nLast transaction:")
    tx = transactions[-1]
    print(f"Date: {tx.date}")
    print(f"Description: {tx.description[:70]}...")
    print(f"Balance: ₹{tx.balance:,.2f}")
else:
    print("No transactions found!")
