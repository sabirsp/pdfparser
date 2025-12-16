from src.idbi_parser import IdbiTransactionParser

parser = IdbiTransactionParser()
transactions = parser.parse_transactions('IDBI_99128926.PDF')

print(f"Total transactions: {len(transactions)}\n")
for t in transactions:
    print(f"{t.date} | {t.description[:50]} | D:{t.debit} C:{t.credit} | Bal:{t.balance}")
