    import { useEffect, useState } from "react";
    import { onAuthStateChanged, User as FirebaseUser } from "firebase/auth";
    import { auth, db } from "../firebase-config";
import { collection, getDocs, query, where } from "firebase/firestore";

    type UsuarioCompleto = {
    uid: string;
    rol: string;
    nombre: string;
    apellido: string;
    dni: string;
    };

    export function useAuth() {
    const [user, setUser] = useState<UsuarioCompleto | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
        if (firebaseUser) {
            // Traemos el rol + datos de Firestore
            try {
            // getRole solo trae rol, entonces mejor obtener todo el doc:
            const usuarioDoc = await getUserData(firebaseUser.uid);
            if (usuarioDoc) {
                setUser({
                uid: firebaseUser.uid,
                rol: usuarioDoc.rol,
                nombre: usuarioDoc.nombre,
                apellido: usuarioDoc.apellido,
                dni: usuarioDoc.dni,
                });
            } else {
                setUser(null);
            }
            } catch (e) {
            setUser(null);
            }
        } else {
            setUser(null);
        }
        setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    return { user, loading };
    }

    // Función para obtener los datos completos del usuario Firestore (rol, nombre, apellido, dni)
    async function getUserData(uid: string): Promise<UsuarioCompleto | null> {
    try {
        const usersRef = collection(db, "usuarios");
        const q = query(usersRef, where("user_uid", "==", uid));
        const querySnapshot = await getDocs(q);

        if (!querySnapshot.empty) {
        const userDoc = querySnapshot.docs[0];
        const data = userDoc.data();
        return {
            uid,
            rol: data.rol,
            nombre: data.nombre,
            apellido: data.apellido,
            dni: userDoc.id,  // El id del documento es el dni
        };
        }
        return null;
    } catch (error) {
        console.error("Error al obtener datos de usuario:", error);
        return null;
    }
}