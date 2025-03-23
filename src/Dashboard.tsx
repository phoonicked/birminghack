import React, { useState, useEffect } from "react";
import "./Dashboard.css"; // Import the Dashboard CSS
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

/** CardProps for the reusable Card component */
interface CardProps {
  title: string;
  value?: string;
  children?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, value, children }) => {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      {value ? <p className="card-value">{value}</p> : children}
    </div>
  );
};

/** ActivityChart: Bar chart with mock hourly data */
const ActivityChart: React.FC = () => {
  const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  const data = {
    labels,
    datasets: [
      {
        label: "Visits",
        data: [5, 10, 8, 12, 15, 7, 3, 4, 8, 16, 20, 18, 10, 5, 2, 0, 3, 7, 9, 11, 14, 16, 12, 8],
        backgroundColor: "#4F90FF", // Blue with good contrast
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Hourly Visits",
        font: { size: 16 },
      },
    },
    scales: {
      y: { beginAtZero: true, ticks: { precision: 0 } },
    },
  };

  return (
    <div
      className="activity-chart-container"
      role="img"
      aria-label="Bar chart showing the number of visits per hour over 24 hours"
    >
      <Bar data={data} options={options} />
    </div>
  );
};

/** Note interface */
interface Note {
  id: string;
  text: string;
  createdAt?: any;
}

/** NotesCard: Manages adding, editing, deleting notes */
const NotesCard: React.FC = () => {
  const [note, setNote] = useState("");
  const [noteMessage, setNoteMessage] = useState("");
  const [notes, setNotes] = useState<Note[]>([]);
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingNoteText, setEditingNoteText] = useState("");

  const fetchNotes = async () => {
    try {
      const notesCollection = collection(db, "notes");
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

  const handleEditNote = (id: string, currentText: string) => {
    setEditingNoteId(id);
    setEditingNoteText(currentText);
  };

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
    <Card title="Notes">
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
                  <button onClick={() => handleUpdateNote(n.id)} className="note-update-btn">
                    <FaCheck />
                  </button>
                  <button onClick={() => setEditingNoteId(null)} className="note-cancel-btn">
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
    </Card>
  );
};

/** Main Dashboard Component */
const Dashboard: React.FC = () => {
  const username = "John Doe"; // Mock username

  return (
    <main className="dashboard">
      <h1 className="dashboard-greeting">Hey, {username}</h1>

      {/* 
        We'll split the layout into two columns:
          - Left column for Alerts + Notes
          - Right column for Activity chart
      */}
      <div className="dashboard-grid">
        <section className="left-column">
          {/* Alerts */}
          <Card title="Alerts" value="You have 5 new alerts" />

          {/* Notes */}
          <NotesCard />
        </section>

        <section className="right-column">
          {/* Activity (Bar Chart) */}
          <Card title="Activity">
            <ActivityChart />
          </Card>
        </section>
      </div>
    </main>
  );
};

export default Dashboard;