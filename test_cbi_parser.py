from src.cbi_parser import CbiTransactionParser

parser = CbiTransactionParser()
transactions = parser.parse_transactions('CBI.pdf')

print(f'Total transactions: {len(transactions)}')
print()

if transactions:
    print('First transaction:')
    tx = transactions[0]
    print(f'  Date: {tx.date}')
    print(f'  Description: {tx.description}')
    print(f'  Debit: {tx.debit:,.2f}')
    print(f'  Credit: {tx.credit:,.2f}')
    print(f'  Balance: {tx.balance:,.2f}')
    print()
    
    print('Last transaction:')
    tx = transactions[-1]
    print(f'  Date: {tx.date}')
    print(f'  Description: {tx.description}')
    print(f'  Debit: {tx.debit:,.2f}')
    print(f'  Credit: {tx.credit:,.2f}')
    print(f'  Balance: {tx.balance:,.2f}')
    print()
    
    opening_balance = transactions[0].balance - transactions[0].credit + transactions[0].debit
    closing_balance = transactions[-1].balance
    
    print(f'Opening Balance: {opening_balance:,.2f}')
    print(f'Closing Balance: {closing_balance:,.2f}')
