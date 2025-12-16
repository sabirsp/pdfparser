import streamlit as st
import requests

# Firebase config
firebase_config = {
    "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8",
    "authDomain": "pdfparser-a63d5.firebaseapp.com",
    "projectId": "pdfparser-a63d5"
}

def create_admin_user():
    """Create admin user in Firebase"""
    st.title("🔧 Setup Admin User")
    
    with st.form("create_admin"):
        admin_email = st.text_input("Admin Email", value="admin@pdfparser.com")
        admin_password = st.text_input("Admin Password", type="password", value="admin123")
        create_btn = st.form_submit_button("Create Admin")
        
        if create_btn:
            try:
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}"
                
                payload = {
                    "email": admin_email,
                    "password": admin_password,
                    "returnSecureToken": True
                }
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    st.success(f"✅ Admin user created: {admin_email}")
                    st.info("Password: admin123")
                    st.info("Now run: streamlit run app_with_registration.py")
                else:
                    st.error("Failed to create admin user")
                    st.json(response.json())
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    create_admin_user()