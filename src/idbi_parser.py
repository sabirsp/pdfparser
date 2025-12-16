import re
import pdfplumber
from .idbi1_parser import Idbi1Parser
from .idbi2_parser import Idbi2Parser

class IdbiTransactionParser:
    def parse_transactions(self, pdf_path, password=None):
        if password is None:
            password = pdf_path.split('_')[-1].replace('.PDF', '').replace('.pdf', '')
        if password and password.lower() == 'none':
            password = ''
        
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and self._is_transaction_table(table):
                        header = [str(cell).lower() if cell else '' for cell in table[0]]
                        header_str = ' '.join(header)
                        if 'txn date' in header_str:
                            return Idbi2Parser().parse_transactions(pdf_path, password)
                        else:
                            return Idbi1Parser().parse_transactions(pdf_path, password)
        return []
    
    def _is_transaction_table(self, table):
        if not table or len(table) < 2:
            return False
        
        header = [str(cell).lower() if cell else '' for cell in table[0]]
        header_str = ' '.join(header)
        return 'date' in header_str and 'withdrawals' in header_str and 'deposits' in header_str
