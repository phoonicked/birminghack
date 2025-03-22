// Contact.tsx
import React, { useState } from 'react';
import { getFirestore, collection, addDoc } from 'firebase/firestore';
import { app } from '../src/api/firebase'; 

interface Contact {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
}

const db = getFirestore(app);

const ContactForm: React.FC = () => {
  const [contact, setContact] = useState<Contact>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
  });

  const [message, setMessage] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setContact((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const docRef = await addDoc(collection(db, 'contacts'), contact);
      setMessage(`Contact added with ID: ${docRef.id}`);
      setContact({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
      });
    } catch (error) {
      console.error('Error adding contact:', error);
      setMessage('Error adding contact.');
    }
  };

  return (
    <div>
      <h2>Add New Contact</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>First Name: </label>
          <input
            type="text"
            name="firstName"
            value={contact.firstName}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Last Name: </label>
          <input
            type="text"
            name="lastName"
            value={contact.lastName}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Email: </label>
          <input
            type="email"
            name="email"
            value={contact.email}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Phone: </label>
          <input
            type="tel"
            name="phone"
            value={contact.phone}
            onChange={handleChange}
          />
        </div>
        <button type="submit">Add Contact</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ContactForm;