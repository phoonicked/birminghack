import React from "react";
import { useEffect, useState } from "react"; 
import { db } from "../src/api/firebase";
import { Routes, Route } from "react-router-dom";
import { collection, getDocs } from "firebase/firestore"
import Dashboard from "./Dashboard"; 
import ContactForm from "./Contacts";

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