import streamlit as st
import json
import requests

def init_firebase():
    """Initialize Firebase config"""
    if 'firebase_config' not in st.session_state:
        st.session_state.firebase_config = {
            "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
            "authDomain": "pdfparser-a63d5.firebaseapp.com",
            "projectId": "pdfparser-a63d5"
        }

def login_form():
    """Simple login form"""
    st.title("🔐 Login")
    
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn and email and password:
            if authenticate(email, password):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def authenticate(email, password):
    """Authenticate with Firebase"""
    try:
        config = st.session_state.firebase_config
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except:
        return False

def is_authenticated():
    """Check if user is logged in"""
    return st.session_state.get('authenticated', False)

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()

def get_user():
    """Get current user email"""
    return st.session_state.get('user_email', '')