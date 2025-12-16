from flask import Flask, request, jsonify
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("../pdfparser-a63d5-firebase-adminsdk-fbsvc-fef1058fff.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    # Register with Firebase Auth
    config = {
        "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8"
    }
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={config['apiKey']}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        # Store in Firestore
        db.collection('users').document(email).set({
            'name': name,
            'email': email,
            'approved': False
        })
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": response.json()})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    config = {
        "apiKey": "AIzaSyDJhE7OExAO1eq_p0caZ4VHn6S29zoc2u8"
    }
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={config['apiKey']}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        # Check approval
        if email == 'admin@pdfparser.com':
            approved = True
        else:
            doc = db.collection('users').document(email).get()
            approved = doc.to_dict().get('approved', False) if doc.exists else False
        
        return jsonify({"success": True, "approved": approved, "token": response.json().get('idToken')})
    
    return jsonify({"success": False})

if __name__ == '__main__':
    app.run()