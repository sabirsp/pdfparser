# tests/test_parser.py
import unittest
import os
from src.bank_parser import IndianBankStatementParser

class TestBankParser(unittest.TestCase):
    def setUp(self):
        self.parser = IndianBankStatementParser()
    
    def test_sbi_statement(self):
        result = self.parser.parse_statement("test_files/sbi_sample.pdf")
        self.assertEqual(result['bank_name'], 'SBI')
        self.assertGreater(result['total_transactions'], 0)
    
    def test_hdfc_statement(self):
        result = self.parser.parse_statement("test_files/hdfc_sample.pdf")
        self.assertEqual(result['bank_name'], 'HDFC')
        self.assertGreater(result['total_transactions'], 0)

if __name__ == '__main__':
    unittest.main()