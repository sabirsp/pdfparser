import streamlit as st
import os
import json
from datetime import datetime
from src.bank_parser import IndianBankStatementParser
from src.tally_export import generate_tally_xml
from src.models import Transaction
import auth_admin as auth

# Initialize Firebase
auth.init_firebase()

# Check authentication
if not auth.is_authenticated():
    auth.auth_form()
    st.stop()

# Admin panel (if admin user)
auth.admin_panel()

# Main app header
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🏦 Bank Statement Parser")
    st.write(f"Welcome, {auth.get_user_name()}")
with col2:
    if st.button("Logout"):
        auth.logout()

st.write("Upload your bank PDF statement to extract transactions")

uploaded_file = st.file_uploader("Choose PDF file", type="pdf")
password = st.text_input("PDF Password (if required)", type="password")

if uploaded_file is not None:
    temp_path = "temp_statement.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    
    try:
        with st.spinner("Parsing statement..."):
            parser = IndianBankStatementParser()
            
            pdf_password = password if password else None
            if not pdf_password and 'IDBI_' in uploaded_file.name:
                pdf_password = uploaded_file.name.split('_')[-1].replace('.PDF', '').replace('.pdf', '')
            
            result = parser.parse_statement(temp_path, password=pdf_password)
        
        st.success(f"✅ Successfully parsed {result['total_transactions']} transactions from {result['bank_name']} Bank")
        
        # Show transactions
        if result['transactions']:
            import pandas as pd
            
            df_data = []
            for tx in result['transactions']:
                desc_parts = tx['description'].split(' | Ref: ')
                description = desc_parts[0]
                reference = desc_parts[1] if len(desc_parts) > 1 else '-'
                
                df_data.append({
                    'Date': tx['date'],
                    'Description': description,
                    'Reference': reference,
                    'Debit (₹)': f"{tx['debit']:,.2f}" if tx['debit'] > 0 else "-",
                    'Credit (₹)': f"{tx['credit']:,.2f}" if tx['credit'] > 0 else "-",
                    'Balance (₹)': f"{tx['balance']:,.2f}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Download options
            st.subheader("📥 Download Results")
            col1, col2 = st.columns(2)
            
            with col1:
                json_str = json.dumps(result, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"parsed_{uploaded_file.name}.json",
                    mime="application/json"
                )
            
            with col2:
                # Tally XML Export
                with st.expander("📤 Export to Tally XML"):
                    bank_ledger_name = st.text_input(
                        "Bank Ledger Name (as in Tally)",
                        help="Enter the exact ledger name as saved in Tally",
                        key=f"ledger_{uploaded_file.name}"
                    )
                    
                    # Pre-populate dates with first and last transaction dates
                    def parse_date(date_str):
                        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d %b %Y', '%d-%b-%Y', '%d/%b/%Y', '%B%d%Y', '%B%d,%Y', '%B%d, %Y']
                        for fmt in formats:
                            try:
                                return datetime.strptime(date_str, fmt).date()
                            except ValueError:
                                continue
                        raise ValueError(f"Unable to parse date: {date_str}")
                    
                    if not result['transactions']:
                        st.warning("No transactions available for Tally export")
                    else:
                        first_date = parse_date(result['transactions'][0]['date'])
                        last_date = parse_date(result['transactions'][-1]['date'])
                        
                        # Ensure from_date is earlier than to_date
                        min_date = min(first_date, last_date)
                        max_date = max(first_date, last_date)
                        
                        col_date1, col_date2 = st.columns(2)
                        with col_date1:
                            from_date = st.date_input("From Date", value=min_date)
                        with col_date2:
                            to_date = st.date_input("To Date", value=max_date)
                        
                        if bank_ledger_name:
                            # Filter transactions by date range
                            filtered_txns = []
                            for tx in result['transactions']:
                                # Convert transaction date string to date object for comparison
                                tx_date = parse_date(tx['date'])
                                if from_date <= tx_date <= to_date:
                                    filtered_txns.append(Transaction(
                                        date=tx_date,
                                        description=tx['description'],
                                        debit=tx['debit'],
                                        credit=tx['credit'],
                                        balance=tx['balance'],
                                        bank_name=tx['bank_name']
                                    ))
                            
                            if filtered_txns:
                                xml_content = generate_tally_xml(filtered_txns, bank_ledger_name)
                                st.download_button(
                                    label=f"Download Tally XML ({len(filtered_txns)} transactions)",
                                    data=xml_content,
                                    file_name=f"tally_{bank_ledger_name}_{from_date}_{to_date}.xml",
                                    mime="application/xml"
                                )
                            else:
                                st.warning("No transactions found in selected date range")
                        else:
                            st.info("Enter Bank Ledger Name to enable Tally XML export")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)