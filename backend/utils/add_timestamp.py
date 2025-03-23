from datetime import datetime, timezone
from .firebase_init import get_firestore_client

def add_timestamp_to_dayharry():
    """
    Adds a new document to the 'dayharry' collection with a 'time' field
    set to the current date/time in a human-readable format.
    """
    db = get_firestore_client()
    current_time = datetime.now(timezone.utc)
    result = db.collection('dayharry').add({
        'time': current_time
    })

    print("New dayharry document created with ID:", result)

if __name__ == '__main__':
    add_timestamp_to_dayharry()
