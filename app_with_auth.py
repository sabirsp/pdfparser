import streamlit as st
import os
import json
from datetime import datetime
from src.bank_parser import IndianBankStatementParser
from src.tally_export import generate_tally_xml
from src.models import Transaction
from firebase_auth import FirebaseAuth

# Firebase configuration (replace with your config)
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "your-private-key",
    "client_email": "your-client-email",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
}

# Initialize Firebase Auth
firebase_auth = FirebaseAuth(FIREBASE_CONFIG)

# Check authentication
if not firebase_auth.is_authenticated():
    firebase_auth.login_form()
    st.stop()

# Main app (only shown to authenticated users)
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🏦 Bank Statement Parser")
with col2:
    if st.button("Logout"):
        firebase_auth.logout()

st.write(f"Welcome, {firebase_auth.get_user_email()}!")
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
        
        # Rest of your existing app code...
        
    except Exception as e:
        st.error(f"❌ Error parsing statement: {str(e)}")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)