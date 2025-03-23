from .firebase_init import get_firestore_client

def fetch_notes():
    """
    Fetches all notes from the 'notes' collection.

    Returns:
        A list of dictionaries, each containing the note's document ID and text.
    """
    db = get_firestore_client()
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
    # Example usage
    notes = fetch_notes()
    print("Fetched notes:")
    for note in notes:
        print(note)
