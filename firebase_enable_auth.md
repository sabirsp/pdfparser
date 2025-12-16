# Enable Firebase Authentication

## Steps to Fix OPERATION_NOT_ALLOWED Error:

1. **Go to Firebase Console**:
   https://console.firebase.google.com/project/pdfparser-a63d5

2. **Navigate to Authentication**:
   - Click "Authentication" in left sidebar
   - Click "Get started" if first time

3. **Enable Email/Password**:
   - Go to "Sign-in method" tab
   - Find "Email/Password" provider
   - Click on it
   - Toggle "Enable" to ON
   - Click "Save"

4. **Run setup again**:
   ```bash
   streamlit run setup_admin.py
   ```

The error occurs because Email/Password authentication is not enabled in your Firebase project.