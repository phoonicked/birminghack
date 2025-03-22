import React from "react";
import { MdDashboard, MdContacts, MdSettings } from "react-icons/md";
import { Link } from "react-router-dom";
import "./Sidebar.css";
 
const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">My Dashboard</div>
      <nav className="nav">
        <ul className="nav-list">
          <li>
            <MdDashboard size={20} />
            <Link to="/">Dashboard</Link>
          </li>
          <li>
            <MdContacts size={20} />
            <Link to="/contacts">Contacts</Link>
          </li>
          <li>
            <MdSettings size={20} />
            <span>Settings</span>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;