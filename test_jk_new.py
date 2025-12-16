import pdfplumber

with pdfplumber.open('JK_BANK.pdf', password='8420641706') as pdf:
    print(f'Total pages: {len(pdf.pages)}')
    print()
    
    page = pdf.pages[0]
    text = page.extract_text()
    print('First 1000 characters:')
    print(text[:1000])
    print()
    
    tables = page.extract_tables()
    print(f'Tables found on page 1: {len(tables)}')
    if tables:
        print()
        print('First table header:')
        print(tables[0][0])
        print()
        print('First 5 data rows:')
        for i, row in enumerate(tables[0][1:6]):
            print(f'Row {i+1}:', row)
