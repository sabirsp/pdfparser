from src.bob_parser import BobTransactionParser

parser = BobTransactionParser()
transactions = parser.parse_transactions('bob_9593597852.pdf', password='9593597852')

print(f"Total transactions: {len(transactions)}\n")
for t in transactions[:10]:
    print(f"{t.date} | {t.description[:50]} | D:{t.debit} C:{t.credit} | Bal:{t.balance}")
