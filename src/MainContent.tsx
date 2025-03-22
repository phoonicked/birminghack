import React from "react";
import { useEffect, useState } from "react"; 
import { db, storage, collection, addDoc, ref, uploadBytes, 
  getDownloadURL, setDoc, getDocs, updateDoc, doc, getDoc  } from "./api/firebase.ts";

//const users: User[] = [
//  { name: "Florence Shaw", email: "florence@example.com", joined: "Mar 4, 2024" },
//  { name: "Amelie Laurent", email: "amelie@example.com", joined: "Mar 5, 2024" },
//  { name: "Sienna May", email: "sienna@example.com", joined: "Mar 7, 2024" },
//];

interface Contact {
  id: string;
  name: string;
  telephone: string;
  image: string;
  time: string;
}

const MainContent: React.FC = () => {

const [contacts, setContacts] = useState<Contact[]>([]);

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

  console.log(contacts);

  return (
    <main className="main-content">
      <div className="main-content-header">
        <h1>User Management</h1>
        <button className="add-user-btn">Add User</button>
      </div>
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

export default MainContent;