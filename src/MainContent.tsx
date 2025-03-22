import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./Dashboard"; 
import ContactForm from "./Contacts";

const MainContent: React.FC = () => {
  return (
    <main className="main-content">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/contacts" element={<ContactForm />} />
      </Routes>
    </main>
  );
};

export default MainContent;