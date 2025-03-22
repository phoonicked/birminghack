import React, { useState, useEffect } from 'react';
import { getFirestore, collection, addDoc, getDocs, serverTimestamp } from 'firebase/firestore';
import { app, db } from '../src/api/firebase';

interface Contact {
    name: string;
    telephone: string;
    time: string;
    id?: string;
}

const Contacts: React.FC = () => {

    const [contact, setContact] = useState<Contact>({
        name: '',
        telephone: '',
        time: '',
        id: '',
    });

    const [contacts, setContacts] = useState<Contact[]>([]);
    const [message, setMessage] = useState<string>('');
    const [showForm, setShowForm] = useState<boolean>(false);

    useEffect(() => {
        fetchContacts();
    }, []);

    const fetchContacts = async () => {
        // Reference to the "contacts" collection
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

    // Handle form submission and add new contact
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            const newContact = { ...contact, createdAt: serverTimestamp() };
            const docRef = await addDoc(collection(db, 'contacts'), newContact);
            setMessage(`Contact added with ID: ${docRef.id}`);
            // Reset form
            setContact({
                name: '',
                telephone: '',
                time: '',
                id: '',
            });
            // Refresh the contacts list
            fetchContacts();
        } catch (error) {
            console.error('Error adding contact:', error);
            setMessage('Error adding contact.');
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
                        <div>
                            <label>First Name: </label>
                            <input
                                type="text"
                                name="firstName"
                                value={contact.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div>
                            <label>Telephone: </label>
                            <input
                                type="email"
                                name="email"
                                value={contact.telephone}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <button type="submit" onClick={handleSubmit()}>Add Contact</button>
                    </form>
                    {message && <p>{message}</p>}
                </div>
            )}
            <div className="table-container">
                <table className="user-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Joined</th>
                        </tr>
                    </thead>
                    <tbody>
                        {contacts.map((contact, idx) => (
                            <tr key={idx}>
                                <td>{contact.name}</td>
                                <td>{contact.telephone}</td>
                                <td>{contact.time}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </main>
    );
};

export default Contacts;