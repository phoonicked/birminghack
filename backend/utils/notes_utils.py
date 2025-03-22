import firebase_admin
from firebase_admin import credentials, firestore

# Initialize the Firebase Admin SDK with your service account key.
cred = credentials.Certificate('../brumhack.json')
firebase_admin.initialize_app(cred)

# Create a Firestore client.
db = firestore.client()

def fetch_notes():
    """
    Fetches all notes from the 'notes' collection.
    
    Returns:
        A list of dictionaries, each containing the note's document ID and text.
    """
    notes_ref = db.collection('notes')
    docs = notes_ref.stream()
    notes = []
    for doc in docs:
        data = doc.to_dict()
        note = {
            'id': doc.id,
            'text': data.get('text', '')
        }
        notes.append(note)
    return notes

if __name__ == '__main__':
    notes = fetch_notes()
    print("Fetched notes:")
    for note in notes:
        print(note)