import React from "react";
import { MdDashboard, MdContacts, MdSettings } from "react-icons/md";

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">My Dashboard</div>
      <nav className="nav">
        <ul className="nav-list">
          <li>
            <MdDashboard size={20} />
            <span>Dashboard</span>
          </li>
          <li>
            <MdContacts size={20} />
            <span>Contacts</span>
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