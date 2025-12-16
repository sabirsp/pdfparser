# src/bank_parser.py
import re
from datetime import datetime
from .pdf_processor import PDFProcessor
from .bank_patterns import BankIdentifier
from .transaction_parser import TransactionParser
from .models import Transaction

class IndianBankStatementParser:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.bank_identifier = BankIdentifier()
        self.transaction_parser = TransactionParser()
    
    def parse_statement(self, pdf_path, password=None):
        print("Step 1: Extracting text from PDF...")
        text = self.pdf_processor.extract_text(pdf_path, password=password)
        
        print("Step 2: Identifying bank...")
        bank_name = self.bank_identifier.identify_bank(text)
        print(f"Identified Bank: {bank_name}")
        
        print("Step 3: Parsing transactions...")
        transactions = self.transaction_parser.parse_transactions(text, bank_name, pdf_path, password=password)
        
        print("Step 4: Generating output...")
        result = {
            'bank_name': bank_name,
            'total_transactions': len(transactions),
            'transactions': [tx.to_dict() for tx in transactions],
            'metadata': self._extract_metadata(text)
        }
        
        return result
    
    def _extract_metadata(self, text):
        # Extract account number, period etc.
        account_match = re.search(r'Account\s*[Nn]o\.?\s*:\s*(\d+)', text)
        return {
            'account_number': account_match.group(1) if account_match else 'Not found',
            'parsed_at': datetime.now().isoformat()
        }