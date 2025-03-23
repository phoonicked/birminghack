import React, { useState, useEffect } from "react";
import {
  collection,
  addDoc,
  getDocs,
  serverTimestamp,
  doc,
  updateDoc,
  deleteDoc,
} from "firebase/firestore";
import { db } from "../src/api/firebase";
import { AiOutlineUserAdd } from "react-icons/ai";
import { FaEdit, FaTrash } from "react-icons/fa"; // Icons for edit & delete
import "./Contacts.css";

interface Contact {
  name: string;
  image: string; // Changed from telephone to image
  notes: string;
  id?: string;
}

const Contacts: React.FC = () => {
  const [contact, setContact] = useState<Contact>({
    name: "",
    image: "",
    notes: "",
  });
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [message, setMessage] = useState<string>("");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    const contactsRef = collection(db, "Contacts");
    const snapshot = await getDocs(contactsRef);
    // Spread document data first, then set id to ensure it's not overridden.
    const contactsList: Contact[] = snapshot.docs.map((docSnap) => ({
      ...(docSnap.data() as Omit<Contact, "id">),
      id: docSnap.id,
    }));
    console.log("Fetched contacts:", contactsList);
    setContacts(contactsList);
  };

  /** Opens the modal with blank fields for adding a new contact. */
  const handleOpenAddModal = () => {
    setContact({ name: "", image: "", notes: "" });
    setEditingId(null);
    setShowModal(true);
  };

  /** Opens the modal with an existing contact's data for editing. */
  const handleEdit = (c: Contact) => {
    setContact(c);
    setEditingId(c.id ?? null);
    setShowModal(true);
  };

  /** Deletes the contact from Firestore, then refreshes the list. */
  const handleDelete = async (id?: string) => {
    console.log("Delete function called with ID:", id);
    if (!id) {
      console.warn("No ID passed to handleDelete");
      return;
    }
    try {
      await deleteDoc(doc(db, "Contacts", id));
      console.log("Successfully deleted doc with ID:", id);
      setMessage("Contact deleted.");
      await fetchContacts();
    } catch (error) {
      console.error("Error deleting contact:", error);
      setMessage("Error deleting contact.");
    }
  };

  /** Updates local state for the form fields. */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setContact((prev) => ({ ...prev, [name]: value }));
  };

  /** Adds or updates a contact in Firestore. */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (editingId) {
        // UPDATE EXISTING CONTACT
        const contactDocRef = doc(db, "Contacts", editingId);
        await updateDoc(contactDocRef, {
          name: contact.name,
          image: contact.image,
          notes: contact.notes,
        });
        setMessage("Contact updated successfully.");
      } else {
        // ADD NEW CONTACT
        const newContact = { ...contact, createdAt: serverTimestamp() };
        const docRef = await addDoc(collection(db, "Contacts"), newContact);
        setMessage(`Contact added with ID: ${docRef.id}`);
      }
      setShowModal(false);
      setEditingId(null);
      setContact({ name: "", image: "", notes: "" });
      await fetchContacts();
    } catch (error) {
      console.error("Error adding/updating contact:", error);
      setMessage("Error adding/updating contact.");
    }
  };

  return (
    <main className="contacts-container">
      {/* Optional tab/pill navigation */}
      <div className="tab-nav">
        <button className="tab-pill active">All Contacts</button>
        <button className="tab-pill">Frequent</button>
        <button className="tab-pill">Favorites</button>
        <button className="tab-pill">Groups</button>
      </div>

      <div className="quick-access-header">
        <h2 className="section-title">Quick Access</h2>
      </div>

      {/* Cards row for displaying contact info */}
      <div className="cards-row">
        {contacts.map((c) => (
          <div key={c.id} className="contact-card">
            <div className="contact-info">
              <h3>{c.name}</h3>
              {/* Display the image instead of telephone text */}
              <img
                className="contact-image"
                src={c.image}
                alt={c.name}
              />
            </div>
            <div className="contact-extra">
              <span className="notes-label">Notes</span>
              <p className="notes-text">{c.notes || "No notes yet"}</p>
            </div>
            {/* Action icons for Edit and Delete */}
            <div className="card-actions">
              <button className="card-btn edit-btn" onClick={() => handleEdit(c)}>
                <FaEdit />
              </button>
              <button className="card-btn delete-btn" onClick={() => handleDelete(c.id)}>
                <FaTrash />
              </button>
            </div>
          </div>
        ))}

        {/* Add-Contact tile at the end of the row */}
        <div className="contact-card add-contact-tile" onClick={handleOpenAddModal}>
          <AiOutlineUserAdd size={36} className="add-contact-icon" />
          <p>Click to add a new contact</p>
        </div>
      </div>

      {/* Modal for Add/Update */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // Prevent modal from closing when clicking inside content
          >
            <h2>{editingId ? "Update Contact" : "Add Contact"}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">Name:</label>
                <input
                  className="input-field"
                  id="name"
                  name="name"
                  type="text"
                  value={contact.name}
                  onChange={handleChange}
                  required
                />
              </div>
              {/* Change label and input from Telephone to Image URL */}
              <div className="form-group">
                <label htmlFor="image">Image URL:</label>
                <input
                  className="input-field"
                  id="image"
                  name="image"
                  type="text"
                  value={contact.image}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="notes">Notes:</label>
                <input
                  className="input-field"
                  id="notes"
                  name="notes"
                  type="text"
                  value={contact.notes}
                  onChange={handleChange}
                />
              </div>
              <button type="submit" className="submit-btn">
                {editingId ? "Update" : "Save"}
              </button>
            </form>
            {message && <p className="message">{message}</p>}
          </div>
        </div>
      )}
    </main>
  );
};

export default Contacts;