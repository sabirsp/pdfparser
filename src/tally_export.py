from datetime import datetime, date
from typing import List
from src.models import Transaction

def generate_tally_xml(transactions: List[Transaction], bank_ledger_name: str) -> str:
    """Generate Tally XML format for bank transactions"""
    
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<ENVELOPE>',
        '    <HEADER>',
        '        <TALLYREQUEST>Import Data</TALLYREQUEST>',
        '    </HEADER>',
        '    <BODY>',
        '        <IMPORTDATA>',
        '            <REQUESTDESC>',
        '                <REPORTNAME>Vouchers</REPORTNAME>',
        '            </REQUESTDESC>',
        '            <REQUESTDATA>'
    ]
    
    for txn in transactions:
        if isinstance(txn.date, str):
            txn_date = datetime.strptime(txn.date, '%Y-%m-%d').date()
        elif isinstance(txn.date, datetime):
            txn_date = txn.date.date()
        else:
            txn_date = txn.date
        
        date_str = txn_date.strftime('%Y%m%d')
        narration = txn.description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if txn.debit and txn.debit > 0:
            # Payment voucher (money going out)
            voucher_type = "Payment"
            suspense_deemed = "Yes"
            suspense_amount = f"-{txn.debit:.2f}"
            bank_deemed = "No"
            bank_amount = f"{txn.debit:.2f}"
        else:
            # Receipt voucher (money coming in)
            voucher_type = "Receipt"
            suspense_deemed = "No"
            suspense_amount = f"{txn.credit:.2f}"
            bank_deemed = "Yes"
            bank_amount = f"-{txn.credit:.2f}"
        
        xml_parts.extend([
            '                <TALLYMESSAGE xmlns:UDF="TallyUDF">',
            f'                    <VOUCHER VCHTYPE="{voucher_type}" ACTION="Create">',
            f'                        <DATE>{date_str}</DATE>',
            f'                        <VOUCHERTYPENAME>{voucher_type}</VOUCHERTYPENAME>',
            f'                        <NARRATION>{narration}</NARRATION>',
            f'                        <PARTYLEDGERNAME>{bank_ledger_name}</PARTYLEDGERNAME>',
            '                        <ALLLEDGERENTRIES.LIST>',
            '                            <LEDGERNAME>Suspense</LEDGERNAME>',
            f'                            <ISDEEMEDPOSITIVE>{suspense_deemed}</ISDEEMEDPOSITIVE>',
            f'                            <AMOUNT>{suspense_amount}</AMOUNT>',
            '                        </ALLLEDGERENTRIES.LIST>',
            '                        <ALLLEDGERENTRIES.LIST>',
            f'                            <LEDGERNAME>{bank_ledger_name}</LEDGERNAME>',
            f'                            <ISDEEMEDPOSITIVE>{bank_deemed}</ISDEEMEDPOSITIVE>',
            f'                            <AMOUNT>{bank_amount}</AMOUNT>',
            '                        </ALLLEDGERENTRIES.LIST>',
            '                    </VOUCHER>',
            '                </TALLYMESSAGE>'
        ])
    
    xml_parts.extend([
        '            </REQUESTDATA>',
        '        </IMPORTDATA>',
        '    </BODY>',
        '</ENVELOPE>'
    ])
    
    return '\n'.join(xml_parts)
