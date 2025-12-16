#!/usr/bin/env python3
from src.bank_parser import IndianBankStatementParser

pdf_path = "Jammu_Kashmir_bank.pdf"

parser = IndianBankStatementParser()
result = parser.parse_statement(pdf_path)

print(f"\n{'='*60}")
print(f"Bank: {result['bank_name']}")
print(f"Total Transactions: {result['total_transactions']}")
print(f"{'='*60}\n")

if result['transactions']:
    print("First 3 transactions:")
    for i, tx in enumerate(result['transactions'][:3], 1):
        print(f"\n{i}. Date: {tx['date']}")
        print(f"   Description: {tx['description'][:60]}...")
        print(f"   Debit: ₹{tx['debit']:,.2f}")
        print(f"   Credit: ₹{tx['credit']:,.2f}")
        print(f"   Balance: ₹{tx['balance']:,.2f}")
    
    print(f"\n\nLast transaction:")
    tx = result['transactions'][-1]
    print(f"Date: {tx['date']}")
    print(f"Balance: ₹{tx['balance']:,.2f}")
else:
    print("No transactions found!")
