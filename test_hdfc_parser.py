from src.hdfc_parser import HdfcTransactionParser

parser = HdfcTransactionParser()
transactions = parser.parse_transactions('HDFC_bank_317016433.pdf', password='317016433')

print(f"Total transactions: {len(transactions)}\n")
for t in transactions[:10]:
    print(f"{t.date} | {t.description[:50]} | D:{t.debit} C:{t.credit} | Bal:{t.balance}")
