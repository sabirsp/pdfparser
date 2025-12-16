import pdfplumber

pdf_path = 'HDFC_bank_317016433.pdf'
password = '317016433'

with pdfplumber.open(pdf_path, password=password) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    table = tables[0]
    row = table[1]
    
    print("Date column:")
    print(repr(row[0]))
    print("\nNarration column:")
    print(repr(row[1]))
    print("\nWithdrawal column:")
    print(repr(row[4]))
    print("\nDeposit column:")
    print(repr(row[5]))
    print("\nBalance column:")
    print(repr(row[6]))
