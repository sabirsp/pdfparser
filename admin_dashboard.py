import streamlit as st
import requests
import json

# Firebase config
firebase_config = {
    "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
    "authDomain": "pdfparser-a63d5.firebaseapp.com",
    "projectId": "pdfparser-a63d5"
}

def admin_login():
    """Admin login form"""
    st.title("👨💼 Admin Dashboard")
    
    with st.form("admin_login"):
        email = st.text_input("Admin Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login as Admin")
        
        if login_btn and email and password:
            if authenticate_admin(email, password):
                st.session_state.admin_authenticated = True
                st.session_state.admin_email = email
                st.rerun()
            else:
                st.error("Invalid admin credentials")

def authenticate_admin(email, password):
    """Authenticate admin user"""
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        return response.status_code == 200 and email == "admin@pdfparser.com"
    except:
        return False

def admin_dashboard():
    """Admin dashboard for user management"""
    st.title("👨💼 Admin Dashboard")
    st.write(f"Welcome, {st.session_state.admin_email}")
    
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    st.subheader("📋 User Management")
    
    # In a real app, you'd fetch from Firestore
    # For demo, using session state
    if 'all_users' not in st.session_state:
        st.session_state.all_users = {}
    
    # Display users
    if st.session_state.all_users:
        for email, info in st.session_state.all_users.items():
            with st.expander(f"👤 {email}"):
                st.write(f"**Name:** {info.get('name', 'N/A')}")
                st.write(f"**Status:** {'✅ Approved' if info.get('approved', False) else '⏳ Pending'}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if not info.get('approved', False):
                        if st.button(f"✅ Approve", key=f"approve_{email}"):
                            st.session_state.all_users[email]['approved'] = True
                            st.success(f"Approved {email}")
                            st.rerun()
                with col2:
                    if st.button(f"❌ Delete", key=f"delete_{email}"):
                        del st.session_state.all_users[email]
                        st.success(f"Deleted {email}")
                        st.rerun()
    else:
        st.info("No users registered yet")

def main():
    if not st.session_state.get('admin_authenticated', False):
        admin_login()
    else:
        admin_dashboard()

if __name__ == "__main__":
    main()