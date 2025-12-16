# main.py
import sys
import os

# Add this at the top
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from bank_parser import IndianBankStatementParser
import json

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_pdf>")
        return
    
    pdf_path = sys.argv[1]
    
    try:
        parser = IndianBankStatementParser()
        result = parser.parse_statement(pdf_path)
        
        # Save result
        output_file = f"parsed_{os.path.basename(pdf_path)}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Successfully parsed {result['total_transactions']} transactions")
        print(f"📁 Output saved to: {output_file}")
        
        # Print first few transactions
        print("\n📋 Sample Transactions:")
        for tx in result['transactions'][:3]:
            print(f"  {tx['date']} | {tx['description'][:30]}... | Debit: {tx['debit']} | Credit: {tx['credit']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()