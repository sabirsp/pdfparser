from src.jk_parser import JKBankTransactionParser

parser = JKBankTransactionParser()
transactions = parser.parse_transactions('JK_BANK.pdf', password='8420641706')

print(f'Total transactions: {len(transactions)}')
print()

if transactions:
    print('First 3 transactions:')
    for i, tx in enumerate(transactions[:3]):
        print(f'{i+1}. Date: {tx.date}, Debit: {tx.debit:,.2f}, Credit: {tx.credit:,.2f}, Balance: {tx.balance:,.2f}')
        print(f'   Desc: {tx.description[:80]}')
    print()
    
    print('Last 3 transactions:')
    for i, tx in enumerate(transactions[-3:], len(transactions)-2):
        print(f'{i}. Date: {tx.date}, Debit: {tx.debit:,.2f}, Credit: {tx.credit:,.2f}, Balance: {tx.balance:,.2f}')
        print(f'   Desc: {tx.description[:80]}')
    print()
    
    opening_balance = transactions[0].balance - transactions[0].credit + transactions[0].debit
    closing_balance = transactions[-1].balance
    
    print(f'Opening Balance: {opening_balance:,.2f}')
    print(f'Closing Balance: {closing_balance:,.2f}')
