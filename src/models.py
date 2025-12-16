# src/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    date: str
    description: str
    debit: float
    credit: float
    balance: float
    bank_name: str
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d') if hasattr(self.date, 'strftime') else str(self.date),
            'description': self.description,
            'debit': self.debit,
            'credit': self.credit,
            'balance': self.balance,
            'bank_name': self.bank_name
        }