import streamlit as st
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, firestore

def init_firebase():
    """Initialize Firebase config"""
    if 'firebase_config' not in st.session_state:
        st.session_state.firebase_config = {
            "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
            "authDomain": "pdfparser-a63d5.firebaseapp.com",
            "projectId": "pdfparser-a63d5"
        }

def auth_form():
    """Login and Registration form"""
    st.title("🔐 Authentication")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn and email and password:
                if authenticate(email, password):
                    if is_user_approved(email):
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.warning("Your account is pending admin approval")
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_name = st.text_input("Full Name")
            register_btn = st.form_submit_button("Register")
            
            if register_btn and reg_email and reg_password and reg_name:
                if register_user(reg_email, reg_password, reg_name):
                    st.success("Registration successful! Please wait for admin approval.")
                else:
                    st.error("Registration failed")

def register_user(email, password, name):
    """Register new user"""
    try:
        config = st.session_state.firebase_config
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Store user info in session for approval tracking
            if 'pending_users' not in st.session_state:
                st.session_state.pending_users = {}
            
            st.session_state.pending_users[email] = {
                "name": name,
                "approved": False,
                "registered_at": str(st.session_state.get('current_time', 'now'))
            }
            return True
        return False
    except:
        return False

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

def is_user_approved(email):
    """Check if user is approved by admin"""
    # For demo purposes, using session state
    # In production, use Firestore database
    if 'approved_users' not in st.session_state:
        st.session_state.approved_users = set()
    
    if 'pending_users' not in st.session_state:
        st.session_state.pending_users = {}
    
    return email in st.session_state.approved_users or email in st.session_state.pending_users and st.session_state.pending_users[email].get('approved', False)

def admin_panel():
    """Admin panel for user approval"""
    if st.session_state.get('user_email') == 'admin@pdfparser.com':  # Admin email
        st.sidebar.title("👨‍💼 Admin Panel")
        
        if 'pending_users' in st.session_state and st.session_state.pending_users:
            st.sidebar.subheader("Pending Approvals")
            
            for email, info in st.session_state.pending_users.items():
                if not info.get('approved', False):
                    st.sidebar.write(f"📧 {email}")
                    st.sidebar.write(f"👤 {info['name']}")
                    
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        if st.button(f"✅ Approve", key=f"approve_{email}"):
                            approve_user(email)
                            st.rerun()
                    with col2:
                        if st.button(f"❌ Reject", key=f"reject_{email}"):
                            reject_user(email)
                            st.rerun()
                    st.sidebar.divider()

def approve_user(email):
    """Approve user"""
    if 'approved_users' not in st.session_state:
        st.session_state.approved_users = set()
    
    st.session_state.approved_users.add(email)
    if email in st.session_state.pending_users:
        st.session_state.pending_users[email]['approved'] = True

def reject_user(email):
    """Reject user"""
    if email in st.session_state.pending_users:
        del st.session_state.pending_users[email]

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