// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore, collection, addDoc, getDocs, doc, getDoc, updateDoc, setDoc } from "firebase/firestore";
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAMkUh9052rtNTNaZIAhekjkoOJIoKzs38",
    authDomain: "brumhack-20e67.firebaseapp.com",
    projectId: "brumhack-20e67",
    storageBucket: "brumhack-20e67.firebasestorage.app",
    messagingSenderId: "753961900880",
    appId: "1:753961900880:web:4eb94db2e2f398733fea55",
    measurementId: "G-MFXG77DEGE",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

export {
  db,
  storage,
  auth,
  collection,
  addDoc,
  getDocs,
  doc,
  getDoc,
  updateDoc,
  setDoc,
  ref,
  uploadBytes,
  getDownloadURL
};