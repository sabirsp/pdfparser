# test_imports.py
try:
    from src.models import Transaction
    from src.bank_parser import IndianBankStatementParser
    from src.transaction_parser import TransactionParser
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")