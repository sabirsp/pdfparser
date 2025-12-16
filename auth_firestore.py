import streamlit as st
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    """Initialize Firebase with Firestore"""
    if 'firebase_config' not in st.session_state:
        st.session_state.firebase_config = {
            "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
            "authDomain": "pdfparser-a63d5.firebaseapp.com",
            "projectId": "pdfparser-a63d5"
        }
    
    # Initialize Firestore (no service account needed for basic operations)
    if not firebase_admin._apps:
        try:
            firebase_admin.initialize_app()
            st.session_state.db = firestore.client()
        except:
            st.session_state.db = None

def register_user(email, password, name):
    """Register user and store in Firestore"""
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
            # Store user info in Firestore
            if st.session_state.get('db'):
                st.session_state.db.collection('users').document(email).set({
                    'name': name,
                    'email': email,
                    'approved': False,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
            return True
        return False
    except:
        return False

def is_user_approved(email):
    """Check if user is approved in Firestore"""
    try:
        if st.session_state.get('db'):
            doc = st.session_state.db.collection('users').document(email).get()
            if doc.exists:
                return doc.to_dict().get('approved', False)
        return False
    except:
        return False

def get_pending_users():
    """Get all pending users from Firestore"""
    try:
        if st.session_state.get('db'):
            users = st.session_state.db.collection('users').where('approved', '==', False).stream()
            return [user.to_dict() for user in users]
        return []
    except:
        return []

def approve_user(email):
    """Approve user in Firestore"""
    try:
        if st.session_state.get('db'):
            st.session_state.db.collection('users').document(email).update({'approved': True})
            return True
        return False
    except:
        return False

def reject_user(email):
    """Delete user from Firestore"""
    try:
        if st.session_state.get('db'):
            st.session_state.db.collection('users').document(email).delete()
            return True
        return False
    except:
        return False