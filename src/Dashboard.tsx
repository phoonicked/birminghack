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
  Timestamp,
  doc,
  updateDoc,
  deleteDoc,
  query,
  where,
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

interface TempData {
  name?: string;
  image?: string;
  isContact?: boolean;
  description?: string;
}

const Card: React.FC<CardProps> = ({ title, value, children }) => {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      {value ? <p className="card-value">{value}</p> : children}
    </div>
  );
};

const AlertBox: React.FC = () => {
  // Local state to store fetched data and loading status
  const [tempData, setTempData] = useState<TempData[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch data from "temp" collection on component mount
  useEffect(() => {
    async function fetchData() {
      try {
        const q = query(collection(db, "Contacts"), where("isContact", "==", false));
        const querySnapshot = await getDocs(q);
        const newData: TempData[] = [];

        querySnapshot.forEach((docSnap) => {
          const data = docSnap.data();
          newData.push({
            id: docSnap.id,
            name: data.name,
            isContact: data.isContact,
            image: data.image,
            description: data.description
          });
        });

        setTempData(newData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data from 'temp': ", error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Handler for when the user chooses "Yes"
  const handleAddToContacts = async (item: TempData) => {
    if (!item.name) return;

    try {
      // Add the stranger to the "contacts" collection
      await updateDoc(doc(db, "Contacts",item.id), {
        name: item.name,
        image: item.image, 
        isContact: true,
        description: item.description,
        // Add any additional fields as needed
      });

      // Update the local state for just this item
      setTempData((prev) =>
        prev.map((d) => (d.id === item.id ? { ...d, isContact: true } : d))
      );
      alert(`${item.name} has been added to your contact list!`);
    } catch (err) {
      console.error("Error adding to contacts: ", err);
      alert("Failed to add to contacts. See console for details.");
    }
  };

  // Handler for when the user chooses "No"
  const handleDismissAlert = async (item: TempData) => {
    try {
      // Update the document to mark as contacted without adding to contacts
      await deleteDoc(doc(db, "Contacts", item.id));

      // Update the local state for just this item so its buttons disappear
      setTempData((prev) =>
        prev.map((d) => (d.id === item.id ? { ...d, isContact: true } : d))
      );
      alert(`You dismissed ${item.name} from contacts.`);
    } catch (err) {
      console.error("Error dismissing alert: ", err);
      alert("Failed to dismiss alert. See console for details.");
    }
  };

  return (
    <Card title="Alerts">
      {loading && <p>Loading alerts...</p>}
      {!loading && tempData.length === 0 && <p className="textquestion">No alerts found.</p>}
      {!loading && tempData.length > 0 && (
         <div className="alerts-container">
        <ul>  
          {tempData.map((item) => (
            <li key={item.id} style={{ marginBottom: "1rem" }}>
              <p className="textquestion">Name: {item.name || "Unknown"}</p>
              {/* Only show the question if this stranger hasn't been processed yet */}
              {!item.isContact && (
                <div>
                  <p className="textquestion">
                    Add {item.name || "this stranger"} to your contact list?
                  </p>
                  <p className="textquestion">
                    Description: {item.description || "No description available."}
                  </p>

                  <div className = "alert-description" style={{ display: "flex", gap: "0.5rem" }}>
                    <button className="alert-button" onClick={() => handleAddToContacts(item)}>
                      Yes
                    </button>
                    <button className="alert-button" onClick={() => handleDismissAlert(item)}>
                      No
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      )}
    </Card>
  );
};


/** ActivityChart: Bar chart with mock hourly data */
const ActivityChart: React.FC = () => {
  const [chartData, setChartData] = useState<any>(null);

  
  useEffect(() => {
    async function fetchData() {
      try {
        const querySnapshot = await getDocs(collection(db, "dayharry"));
        const counts = new Array(24).fill(0);

        querySnapshot.forEach((doc) => {
          const data = doc.data();

          if (data.time) {
            let date: Date;

            // 1. If it's already a Firestore Timestamp
            if (data.time instanceof Timestamp) {
              date = data.time.toDate()
            }
            // 2. If it's an object with { seconds, nanoseconds } but not recognized as an instance of Timestamp
            else if (
              typeof data.time === "object" &&
              data.time.seconds !== undefined &&
              data.time.nanoseconds !== undefined
            ) {
              // Construct a Timestamp manually
              const ts = new Timestamp(data.time.seconds, data.time.nanoseconds);
              date = ts.toDate();
            }
            // 3. Otherwise, assume it's a string
            else {
              date = new Date(data.time);
            }

            // If it's a valid date, increment the corresponding hour
            if (!isNaN(date.getTime())) {
              const hour = date.getHours();
              counts[hour]++;
            }
          }
        });

        const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);

        setChartData({
          labels,
          datasets: [
            {
              label: "Visits",
              data: counts,
              backgroundColor: "#4F90FF",
            },
          ],
        });
      } catch (error) {
        console.error("Error fetching data: ", error);
      }
    }

    fetchData();
  }, []);

  if (!chartData) {
    return <div>Loading...</div>;
  }

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
      <Bar data={chartData} options={options} />
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
          <AlertBox />
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