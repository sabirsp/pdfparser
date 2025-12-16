import streamlit as st
import os
import json
from datetime import datetime
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

st.info("📄 PDF parsing functionality will be added after successful deployment")
st.write("This is a demo version for deployment testing")

# Simple file uploader for testing
uploaded_file = st.file_uploader("Choose PDF file", type="pdf")

if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.info("PDF processing will be implemented after deployment")
    
    # Mock result for testing
    mock_result = {
        "bank_name": "Demo Bank",
        "total_transactions": 5,
        "transactions": [
            {"date": "2024-01-01", "description": "Demo Transaction", "debit": 100.0, "credit": 0.0, "balance": 1000.0}
        ]
    }
    
    st.json(mock_result)