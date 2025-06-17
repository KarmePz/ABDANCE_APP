import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Tu configuración
const firebaseConfig = {
  apiKey: "AIzaSyD8eM35C3Vp1anY-IVixAanEj4zx6vZdoY",
  authDomain: "snappy-striker-455715-q2.firebaseapp.com",
  projectId: "snappy-striker-455715-q2",
  storageBucket: "snappy-striker-455715-q2.appspot.com",
  messagingSenderId: "67580882339",
  appId: "1:67580882339:web:87857d1378c8c6742f0216"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Exportar los módulos que usás
export const auth = getAuth(app);
export const db = getFirestore(app);
