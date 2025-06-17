    import { useEffect, useState } from "react";

    type Student = {
    dni: string;
    nombre: string;
    apellido: string;
    email: string;
    rol: string;
    };
    
    export function useDisciplinaStudents(apiUrl: string, disciplinaId: string, reloadFlag = 0) {
    const [students, setStudents] = useState<Student[]>([]);
    const [nombreDisciplina, setNombreDisciplina] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!disciplinaId) return;

        const fetchStudents = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${apiUrl}/disciplinas?disciplina_id=${disciplinaId}`, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            });

            const data = await res.json();
            setStudents(data.alumnos_inscriptos);
            setNombreDisciplina(data.nombre);
        } catch (err) {
            console.error("Error al cargar alumnos:", err);
        } finally {
            setLoading(false);
        }
        };

        fetchStudents();
    }, [apiUrl, disciplinaId, reloadFlag]);

    return { students, nombreDisciplina, loading };
    }