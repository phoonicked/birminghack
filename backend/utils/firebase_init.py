import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore_client(json_key_path="./brumhack.json"):
    """
    Initializes and returns a Firestore client using the given service account key.
    """
    # Initialize the Firebase Admin SDK if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_key_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()
