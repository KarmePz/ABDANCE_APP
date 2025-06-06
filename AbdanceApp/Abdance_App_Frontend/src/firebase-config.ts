// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore } from "firebase/firestore";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD8eM35C3Vp1anY-IVixAanEj4zx6vZdoY",
  authDomain: "snappy-striker-455715-q2.firebaseapp.com",
  projectId: "snappy-striker-455715-q2",
  storageBucket: "snappy-striker-455715-q2.firebasestorage.app",
  messagingSenderId: "675808082339",
  appId: "1:675808082339:web:87857d1378c86b742f0216"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, signInWithEmailAndPassword, db};