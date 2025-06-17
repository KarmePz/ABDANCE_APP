import { useEffect, useState } from "react";

export type Disciplina = {
    disciplina_id: string;
    nombre: string;
};

export function useDisciplinaList(apiUrl: string) {
    const [disciplinas, setDisciplinas] = useState<Disciplina[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
    const fetchDisciplinas = async () => {
        try {
        const res = await fetch(`${apiUrl}/disciplinas`, {
            headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
        });
        const data = await res.json();
        setDisciplinas(data);
        } catch (err) {
        console.error("Error al cargar disciplinas:", err);
        } finally {
        setLoading(false);
        }
    };

    fetchDisciplinas();
    }, [apiUrl]);

    return { disciplinas, loading };
}