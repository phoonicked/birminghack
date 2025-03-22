import "./App.css";
import Sidebar from "./Sidebar";
import MainContent from "./MainContent";
import { BrowserRouter as Router } from "react-router-dom";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <MainContent />
      </div>
    </Router>
  );
}

export default App;
