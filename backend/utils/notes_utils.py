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

def get_contact_name_from_db(contact_id):
    """
    Fetches the contact name from Firestore using the contact ID.

    Args:
        contact_id (str): The unique ID of the contact.

    Returns:
        str: The contact's name if found, otherwise None.
    """
    db = get_firestore_client()
    doc_ref = db.collection("contacts").document(contact_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("name")
    return None