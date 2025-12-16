import firebase_admin
from firebase_admin import credentials, firestore

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("pdfparser-a63d5-firebase-adminsdk-fbsvc-fef1058fff.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Test write
    db.collection('test').document('test').set({'message': 'Hello Firestore!'})
    print("✅ Write successful")
    
    # Test read
    doc = db.collection('test').document('test').get()
    if doc.exists:
        print(f"✅ Read successful: {doc.to_dict()}")
    
    # Clean up
    db.collection('test').document('test').delete()
    print("✅ Firestore connection working!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")