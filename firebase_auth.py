import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json

class FirebaseAuth:
    def __init__(self, firebase_config):
        """Initialize Firebase Auth with config"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
    
    def login_form(self):
        """Display login form and handle authentication"""
        st.title("🔐 Login Required")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if self.authenticate_user(email, password):
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    def authenticate_user(self, email, password):
        """Authenticate user with Firebase"""
        try:
            # For client-side auth, you'd use Firebase JS SDK
            # This is a simplified server-side approach
            user = auth.get_user_by_email(email)
            return True  # Implement actual password verification
        except:
            return False
    
    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.rerun()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_user_email(self):
        """Get current user email"""
        return st.session_state.get('user_email', None)