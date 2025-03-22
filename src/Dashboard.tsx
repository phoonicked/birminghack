import React, { useState, useEffect } from "react";
import "./Dashboard.css"; // Import the Dashboard CSS
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
import { FaEdit, FaTrash, FaCheck, FaTimes } from "react-icons/fa";

interface CardProps {
  title: string;
  value: string;
}

interface Note {
  id: string;
  text: string;
  createdAt?: any;
}

const Card: React.FC<CardProps> = ({ title, value }) => {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      <p className="card-value">{value}</p>
    </div>
  );
};

const NotesCard: React.FC = () => {
  // State for creating a new note
  const [note, setNote] = useState("");
  const [noteMessage, setNoteMessage] = useState("");

  // State for fetched notes
  const [notes, setNotes] = useState<Note[]>([]);

  // State for editing a note
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingNoteText, setEditingNoteText] = useState("");

  // Fetch notes from Firestore
  const fetchNotes = async () => {
    try {
      const notesCollection = collection(db, "generalNotes");
      const snapshot = await getDocs(notesCollection);
      const notesList: Note[] = snapshot.docs.map((docSnap) => ({
        id: docSnap.id,
        ...docSnap.data(),
      })) as Note[];
      setNotes(notesList);
    } catch (error) {
      console.error("Error fetching notes:", error);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  // Add new note
  const handleNoteSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const docRef = await addDoc(collection(db, "notes"), {
        text: note,
        createdAt: serverTimestamp(),
      });
      setNoteMessage(`Note added with ID: ${docRef.id}`);
      setNote("");
      fetchNotes();
    } catch (error) {
      console.error("Error adding note:", error);
      setNoteMessage("Error adding note.");
    }
  };

  // Delete a note
  const handleDeleteNote = async (id: string) => {
    try {
      await deleteDoc(doc(db, "notes", id));
      setNoteMessage("Note deleted successfully.");
      fetchNotes();
    } catch (error) {
      console.error("Error deleting note:", error);
      setNoteMessage("Error deleting note.");
    }
  };

  // Start editing a note
  const handleEditNote = (id: string, currentText: string) => {
    setEditingNoteId(id);
    setEditingNoteText(currentText);
  };

  // Update an existing note
  const handleUpdateNote = async (id: string) => {
    try {
      const noteRef = doc(db, "notes", id);
      await updateDoc(noteRef, { text: editingNoteText });
      setNoteMessage("Note updated successfully.");
      setEditingNoteId(null);
      setEditingNoteText("");
      fetchNotes();
    } catch (error) {
      console.error("Error updating note:", error);
      setNoteMessage("Error updating note.");
    }
  };

  return (
    <div className="card notes-card">
      <h2 className="card-title">Notes</h2>
      <form onSubmit={handleNoteSubmit} className="notes-form">
        <textarea
          className="notes-textarea"
          placeholder="Enter instructions or notes..."
          value={note}
          onChange={(e) => setNote(e.target.value)}
          required
        ></textarea>
        <button type="submit" className="notes-submit-btn">
          Submit Note
        </button>
      </form>
      {noteMessage && <p className="note-message">{noteMessage}</p>}
      <div className="notes-list">
        {notes.map((n) => (
          <div key={n.id} className="note-item">
            {editingNoteId === n.id ? (
              <>
                <textarea
                  className="note-edit-textarea"
                  value={editingNoteText}
                  onChange={(e) => setEditingNoteText(e.target.value)}
                />
                <div className="note-actions">
                  <button
                    onClick={() => handleUpdateNote(n.id)}
                    className="note-update-btn"
                  >
                    <FaCheck />
                  </button>
                  <button
                    onClick={() => setEditingNoteId(null)}
                    className="note-cancel-btn"
                  >
                    <FaTimes />
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="note-text">{n.text}</p>
                <div className="note-actions">
                <button onClick={() => handleEditNote(n.id, n.text)} className="note-edit-btn">
  <FaEdit />
</button>
<button onClick={() => handleDeleteNote(n.id)} className="note-delete-btn">
  <FaTrash />
</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const username = "John Doe"; // Mock username

  return (
    <div className="dashboard">
      <h1 className="dashboard-greeting">Hey, {username}</h1>
      <div className="cards-grid">
        {/* 1) Left-Top: Alerts */}
        <Card title="Alerts" value="You have 5 new alerts" />
        {/* 2) Right (spans two rows): Activity */}
        <Card title="Activity" value="Active for 3 hours today" />
        {/* 3) Left-Bottom: Notes with embedded form and list */}
        <NotesCard />
      </div>
    </div>
  );
};

export default Dashboard;