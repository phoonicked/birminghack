import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./Dashboard"; 
import Contacts from "./Contacts";

const MainContent: React.FC = () => {
  return (
    <main className="main-content">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/contacts" element={<Contacts />} />
      </Routes>
    </main>
  );
};

export default MainContent;