import pdfplumber

pdf_path = 'bob_9593597852.pdf'
password = '9593597852'

with pdfplumber.open(pdf_path, password=password) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    table = tables[0]
    print("First 3 data rows:\n")
    for i in range(1, 4):
        row = table[i]
        print(f"Row {i}:")
        for j, cell in enumerate(row):
            print(f"  Col {j}: {repr(cell)}")
        print()
