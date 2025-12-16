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
            
            # Download JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"parsed_{uploaded_file.name}.json",
                mime="application/json"
            )
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)