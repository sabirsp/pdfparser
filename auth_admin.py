import streamlit as st
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, firestore

def init_firebase():
    """Initialize Firebase with Admin SDK"""
    if 'firebase_config' not in st.session_state:
        st.session_state.firebase_config = {
            "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
            "authDomain": "pdfparser-a63d5.firebaseapp.com",
            "projectId": "pdfparser-a63d5"
        }
    
    # Initialize Firebase only once globally
    if 'firebase_initialized' not in st.session_state:
        try:
            if not firebase_admin._apps:
                # Try to use service account file first
                import os
                if os.path.exists("pdfparser-a63d5-firebase-adminsdk-fbsvc-fef1058fff.json"):
                    cred = credentials.Certificate("pdfparser-a63d5-firebase-adminsdk-fbsvc-fef1058fff.json")
                else:
                    # Use environment variables for deployment
                    firebase_config = {
                        "type": "service_account",
                        "project_id": "pdfparser-a63d5",
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                    cred = credentials.Certificate(firebase_config)
                
                firebase_admin.initialize_app(cred, {
                    'projectId': 'pdfparser-a63d5'
                })
            
            # Always create new Firestore client
            st.session_state.db = firestore.client()
            st.session_state.firebase_initialized = True
            
        except Exception as e:
            st.error(f"❌ Firebase init error: {str(e)}")
            st.session_state.db = None
            st.session_state.firebase_initialized = False
    
    # Ensure db is available even if already initialized
    if 'db' not in st.session_state and firebase_admin._apps:
        try:
            st.session_state.db = firestore.client()
        except:
            st.session_state.db = None

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
    """Register new user and store in Firestore"""
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
            # Store in Firestore
            if st.session_state.get('db'):
                try:
                    st.session_state.db.collection('users').document(email).set({
                        'name': name,
                        'email': email,
                        'approved': False,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })
                    st.success(f"User {email} stored in Firestore")
                except Exception as e:
                    st.error(f"Firestore error: {str(e)}")
            else:
                st.error("Database not connected")
            return True
        else:
            st.error(f"Registration failed: {response.json()}")
        return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
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
    """Check if user is approved in Firestore"""
    # Admin is always approved
    if email == 'admin@pdfparser.com':
        return True
        
    try:
        if st.session_state.get('db'):
            doc = st.session_state.db.collection('users').document(email).get()
            if doc.exists:
                user_data = doc.to_dict()
                approved = user_data.get('approved', False)
                st.info(f"Debug: User {email} found in Firestore, approved: {approved}")
                return approved
            else:
                st.warning(f"Debug: User {email} not found in Firestore")
        else:
            st.error("Debug: Firestore database not connected")
        return False
    except Exception as e:
        st.error(f"Debug: Error checking approval for {email}: {str(e)}")
        return False

def admin_panel():
    """Admin panel for user approval"""
    if st.session_state.get('user_email') == 'admin@pdfparser.com':
        st.sidebar.title("👨💼 Admin Panel")
        
        try:
            if st.session_state.get('db'):
                users = st.session_state.db.collection('users').where('approved', '==', False).stream()
                pending_users = [user.to_dict() for user in users]
                
                if pending_users:
                    st.sidebar.subheader("Pending Approvals")
                    
                    for user in pending_users:
                        email = user['email']
                        name = user['name']
                        
                        st.sidebar.write(f"📧 {email}")
                        st.sidebar.write(f"👤 {name}")
                        
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
                else:
                    # Show all users for debugging
                    all_users = st.session_state.db.collection('users').stream()
                    all_users_list = [user.to_dict() for user in all_users]
                    
                    st.sidebar.write(f"Total users: {len(all_users_list)}")
                    
                    for user in all_users_list:
                        email = user['email']
                        approved = user.get('approved', False)
                        st.sidebar.write(f"📧 {email} - {'✅' if approved else '⏳'}")
                    
                    st.sidebar.info("No pending approvals")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

def approve_user(email):
    """Approve user in Firestore"""
    try:
        if st.session_state.get('db'):
            st.session_state.db.collection('users').document(email).update({'approved': True})
    except:
        pass

def reject_user(email):
    """Delete user from Firestore"""
    try:
        if st.session_state.get('db'):
            st.session_state.db.collection('users').document(email).delete()
    except:
        pass

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

def get_user_name():
    """Get current user name from Firestore"""
    email = st.session_state.get('user_email', '')
    if not email:
        return ''
    
    # Admin user
    if email == 'admin@pdfparser.com':
        return 'Admin'
    
    # Get name from Firestore
    try:
        if st.session_state.get('db'):
            doc = st.session_state.db.collection('users').document(email).get()
            if doc.exists:
                return doc.to_dict().get('name', email)
    except:
        pass
    
    return email