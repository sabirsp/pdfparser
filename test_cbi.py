import pdfplumber

with pdfplumber.open('CBI.pdf') as pdf:
    print(f'Total pages: {len(pdf.pages)}')
    print()
    
    for page_num in range(min(3, len(pdf.pages))):
        page = pdf.pages[page_num]
        tables = page.extract_tables()
        print(f'Page {page_num + 1}: {len(tables)} tables')
        
        if tables and len(tables[0]) > 0:
            print(f'  Header: {tables[0][0]}')
            if len(tables[0]) > 1:
                print(f'  First row: {tables[0][1]}')
        print()
