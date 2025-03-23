from .firebase_init import get_firestore_client

def check_is_contact(name):
    db = get_firestore_client()
    contacts_ref = db.collection('Contacts')
    
    # Query for contacts with the given name
    query = contacts_ref.where('name', '==', name)
    docs = query.stream()
    
    # Check if any matching contact has isContact set to true
    for doc in docs:
        data = doc.to_dict()
        if data.get('isContact', False) == True:
            return True
    
    # No matching contact with isContact=true found
    return False

if __name__ == '__main__':
    # Example usage
    test_name = "Matthew"
    result = check_is_contact(test_name)
    print(f"Is {test_name} a contact? {result}")