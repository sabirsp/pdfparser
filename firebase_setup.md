# Firebase Setup Instructions

## 1. Create Firebase Project
1. Go to https://console.firebase.google.com/
2. Click "Create a project"
3. Enter project name and continue

## 2. Enable Authentication
1. In Firebase console, go to "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable "Email/Password"

## 3. Get Configuration
1. Go to Project Settings (gear icon)
2. Scroll to "Your apps" section
3. Click "Web" icon to add web app
4. Copy the config object

## 4. Update auth.py
Replace the firebase_config in auth.py with your config:

```python
st.session_state.firebase_config = {
    "apiKey": "your-actual-api-key",
    "authDomain": "your-project.firebaseapp.com", 
    "projectId": "your-project-id"
}
```

## 5. Create Test User
1. In Firebase console, go to "Authentication" > "Users"
2. Click "Add user"
3. Enter email and password

## 6. Run App
```bash
streamlit run app_auth.py
```