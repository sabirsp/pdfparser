# src/transaction_parser.py
import re
from datetime import datetime
from .models import Transaction
from .axis_parser import AxisTransactionParser
from .yes_parser import YesTransactionParser
from .yes_parser_fixed import YesTransactionParserFixed
from .yes_text_parser import YesTextParser
from .yes_hybrid_parser import YesHybridParser
from .iob_parser import IOBTransactionParser
from .bandhan_parser import BandhanTransactionParser
from .hsbc_parser import HSBCTransactionParser
from .union_parser import UnionTransactionParser
from .indian_parser import IndianBankTransactionParser
from .federal_parser import FederalTransactionParser
from .jk_parser import JKBankTransactionParser
from .sbi_parser import parse_sbi_statement
from .idbi_parser import IdbiTransactionParser
from .bob_parser import BobTransactionParser
from .hdfc_parser import HdfcTransactionParser
from .pnb_parser import PnbTransactionParser
from .cbi_parser import CbiTransactionParser
from .karnataka_parser import KarnatakaTransactionParser
from .kotak_parser import KotakTransactionParser
from .canara_parser import CanaraTransactionParser
from .indusind_parser import IndusIndTransactionParser

class TransactionParser:
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\d{2,4}-\d{1,2}-\d{1,2}'
        ]
        
        self.amount_pattern = r'[+-]?\d{1,3}(?:,\d{3})*\.?\d{0,2}'
    
    def parse_transactions(self, text, bank_name, pdf_path=None, password=None):
        if bank_name == 'AXIS' and pdf_path:
            axis_parser = AxisTransactionParser()
            return axis_parser.parse_transactions(pdf_path)
        elif bank_name == 'YES' and pdf_path:
            yes_parser = YesHybridParser()
            return yes_parser.parse_transactions(pdf_path)
        elif bank_name == 'IOB' and pdf_path:
            iob_parser = IOBTransactionParser()
            return iob_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'BANDHAN' and pdf_path:
            bandhan_parser = BandhanTransactionParser()
            return bandhan_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'HSBC' and pdf_path:
            hsbc_parser = HSBCTransactionParser()
            return hsbc_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'UNION' and pdf_path:
            union_parser = UnionTransactionParser()
            return union_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'INDIAN' and pdf_path:
            indian_parser = IndianBankTransactionParser()
            return indian_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'FEDERAL' and pdf_path:
            federal_parser = FederalTransactionParser()
            return federal_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'JK' and pdf_path:
            jk_parser = JKBankTransactionParser()
            return jk_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'SBI' and pdf_path:
            return parse_sbi_statement(pdf_path, password=password)
        elif bank_name == 'IDBI' and pdf_path:
            idbi_parser = IdbiTransactionParser()
            return idbi_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'BOB' and pdf_path:
            bob_parser = BobTransactionParser()
            return bob_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'HDFC' and pdf_path:
            hdfc_parser = HdfcTransactionParser()
            return hdfc_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'PNB' and pdf_path:
            pnb_parser = PnbTransactionParser()
            return pnb_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'CBI' and pdf_path:
            cbi_parser = CbiTransactionParser()
            return cbi_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'KARNATAKA' and pdf_path:
            karnataka_parser = KarnatakaTransactionParser()
            return karnataka_parser.extract_transactions(pdf_path, password=password)
        elif bank_name == 'KOTAK' and pdf_path:
            kotak_parser = KotakTransactionParser()
            return kotak_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'CANARA' and pdf_path:
            canara_parser = CanaraTransactionParser()
            return canara_parser.parse_transactions(pdf_path, password=password)
        elif bank_name == 'INDUSIND' and pdf_path:
            indusind_parser = IndusIndTransactionParser()
            return indusind_parser.parse_transactions(pdf_path, password=password)
        
        lines = text.split('\n')
        transactions = []
        
        for line in lines:
            if self._is_transaction_line(line):
                transaction = self._parse_line(line, bank_name)
                if transaction:
                    transactions.append(transaction)
        
        return transactions
    
    def _is_transaction_line(self, line):
        # Check if line has date and amount (likely a transaction)
        has_date = any(re.search(pattern, line) for pattern in self.date_patterns)
        has_amount = re.search(self.amount_pattern, line)
        return has_date and has_amount
    
    def _parse_line(self, line, bank_name):
        try:
            # Extract date
            date = self._extract_date(line)
            if not date:
                return None
            
            # Extract amounts
            amounts = re.findall(self.amount_pattern, line)
            amounts = [float(amt.replace(',', '')) for amt in amounts]
            
            # Extract description (text between date and first amount)
            date_end = line.find(date) + len(date)
            amount_start = line.find(str(amounts[0])) if amounts else len(line)
            description = line[date_end:amount_start].strip()
            
            # Determine debit/credit based on bank logic
            debit, credit, balance = self._determine_amounts(amounts, bank_name)
            
            return Transaction(
                date=date,
                description=description,
                debit=debit,
                credit=credit,
                balance=balance,
                bank_name=bank_name
            )
        except Exception as e:
            print(f"Error parsing line: {line}, Error: {e}")
            return None
    
    def _extract_date(self, line):
        for pattern in self.date_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        return None
    
    def _determine_amounts(self, amounts, bank_name):
        # Simple logic - you'll enhance this based on bank patterns
        if len(amounts) >= 3:
            return amounts[0], amounts[1], amounts[2]
        elif len(amounts) == 2:
            return amounts[0], 0, amounts[1]
        else:
            return 0, amounts[0], amounts[0] if amounts else 0