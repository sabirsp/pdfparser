#!/usr/bin/env python3
# test_iob.py
from src.bank_parser import IndianBankStatementParser

pdf_path = "Indian_Overseas_bank_51087192.pdf"
password = "51087192"

parser = IndianBankStatementParser()
result = parser.parse_statement(pdf_path, password=password)

print(f"\n{'='*60}")
print(f"Bank: {result['bank_name']}")
print(f"Total Transactions: {result['total_transactions']}")
print(f"{'='*60}\n")

if result['transactions']:
    print("First 5 transactions:")
    for i, tx in enumerate(result['transactions'][:5], 1):
        print(f"\n{i}. Date: {tx['date']}")
        print(f"   Description: {tx['description']}")
        print(f"   Debit: ₹{tx['debit']:,.2f}")
        print(f"   Credit: ₹{tx['credit']:,.2f}")
        print(f"   Balance: ₹{tx['balance']:,.2f}")
    
    print(f"\n\nLast transaction:")
    tx = result['transactions'][-1]
    print(f"Date: {tx['date']}")
    print(f"Description: {tx['description']}")
    print(f"Balance: ₹{tx['balance']:,.2f}")
else:
    print("No transactions found!")
