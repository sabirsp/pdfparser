#!/usr/bin/env python3
from src.bank_parser import IndianBankStatementParser
parser = IndianBankStatementParser()
result = parser.parse_statement('Bandhan_bank.pdf')

print('GST Transactions:')
for i, tx in enumerate(result['transactions']):
    if 'GST' in tx['description']:
        print(f'\nTransaction {i+1}:')
        print(f'Date: {tx["date"]}')
        print(f'Description: {tx["description"]}')
        print(f'Debit: ₹{tx["debit"]:,.2f}')
        print(f'Credit: ₹{tx["credit"]:,.2f}')
        print(f'Balance: ₹{tx["balance"]:,.2f}')
