import React, { useState, useEffect } from 'react';
import { collection, addDoc, getDocs, serverTimestamp, doc, updateDoc } from 'firebase/firestore';
import { db } from '../src/api/firebase';
import './Contacts.css';

interface Contact {
    name: string;
    telephone: string;
    notes : string;
}

const Contacts: React.FC = () => {
  const [contact, setContact] = useState<Contact>({
    name: '',
    telephone: '',
    notes: '',
  });
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [message, setMessage] = useState<string>('');
  const [showForm, setShowForm] = useState<boolean>(false);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    // Reference to the "Contacts" collection
    const contactsRef = collection(db, "Contacts");
    const snapshot = await getDocs(contactsRef);

    // Map through the documents to extract each contact's id and data
    const contactsList: Contact[] = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...(doc.data() as Omit<Contact, "id">),
    }));

    // Update state with the fetched contacts
    setContacts(contactsList);
  };

  // Update form state on input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setContact((prev) => ({ ...prev, [name]: value }));
  };

  const handleNotes = async (e: React.ChangeEvent<HTMLInputElement>) => {
        
  }

    // Handle form submission and add new contact
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      try {
        // Check if a contact with the same name or telephone already exists.
        const existingContact = contacts.find(
          (c) => c.name === contact.name || c.telephone === contact.telephone
        );
        console.log(existingContact);
        if (existingContact) {
          // Prompt the user whether to update the existing contact.
          const shouldUpdate = window.confirm(
            "A contact with this name or telephone already exists. Do you want to update it?"
          );
        if (shouldUpdate) {
          // Find the document ID for the existing contact.
          let docId = "";
          const allContacts = collection(db, "Contacts");
          const documents = await getDocs(allContacts);
          documents.forEach((docSnapshot) => {
            const data = docSnapshot.data();
            if (data.name === existingContact.name && data.telephone === existingContact.telephone) {
              docId = docSnapshot.id;
            }
          });

          const contactDocRef = doc(db, "Contacts", docId);
          // Determine which fields to update.
          if (existingContact.name === contact.name && existingContact.telephone !== contact.telephone) {
            await updateDoc(contactDocRef, {
              telephone: contact.telephone,
            });
            setMessage(`Telephone updated for contact with name ${contact.name}.`);
          } else if (existingContact.telephone === contact.telephone && existingContact.name !== contact.name) {
            await updateDoc(contactDocRef, {
              name: contact.name,
            });
            setMessage(`Name updated for contact with telephone ${contact.telephone}.`);
          } else {
            await updateDoc(contactDocRef, {
              name: contact.name,
              telephone: contact.telephone,
            });
            setMessage("Contact updated with new name and telephone.");
          }
          fetchContacts();
          
          } else {
            setMessage("Contact not updated.");
            return;
          }
    
          // If no matching contact exists, add a new contact.
          const newContact = { ...contact };
          const docRef = await addDoc(collection(db, "Contacts"), newContact);
          setMessage(`Contact added with ID: ${docRef.id}`);
          // Reset the form.
          setContact({
           name: "",
            telephone: "",
           notes: "",
          });
          // Refresh the contacts list.
          fetchContacts();
        } catch (error) {
          console.error("Error adding/updating contact:", error);
          setMessage("Error adding/updating contact.");
        }

      // If no matching contact exists, add a new contact.
      const newContact = { ...contact, createdAt: serverTimestamp() };
      const docRef = await addDoc(collection(db, "Contacts"), newContact);
      setMessage(`Contact added with ID: ${docRef.id}`);
      // Reset the form.
      setContact({
        name: "",
        telephone: "",
        notes: "",
      });
      // Refresh the contacts list.
      fetchContacts();
    } 
      catch (error) {
        console.error("Error adding/updating contact:", error);
        setMessage("Error adding/updating contact.");
    }
  };

  return (
    <main className="main-content">
      <div className="main-content-header">
        <h1>User Management</h1>
        <button className="add-user-btn" onClick={() => setShowForm((prev) => !prev)}>
          {showForm ? 'Close Form' : 'Add User'}
        </button>
      </div>
      {showForm && (
        <div className="add-contact-form">
          <h2>Add New Contact</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">First Name:</label>
              <input
                type="text"
                id="name"
                name="name"
                value={contact.name}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
            <div className="form-group">
              <label htmlFor="telephone">Telephone:</label>
              <input
                type="text"
                id="telephone"
                name="telephone"
                value={contact.telephone}
                onChange={handleChange}
                required
                className="input-field"
              />
            </div>
            <button type="submit" className="submit-btn">Add Contact</button>
          </form>
          {message && <p className="message">{message}</p>}
        </div>
      )}
      <div className="table-container">
        <table className="user-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Telephone</th>
            </tr>
          </thead>
          <tbody>
            {contacts.map((contact, idx) => (
              <tr key={idx}>
                <td>{contact.name}</td>
                <td>{contact.telephone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

export default Contacts;