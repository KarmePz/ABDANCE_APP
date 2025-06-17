import { useState, useEffect } from "react";
import { useAuthFetch } from "./useAuthFetch";

// src/hooks/useFetchInasistencias.ts


export type Inasistencia = {
    id: string;
    fecha: string;
    justificada: string;
};

    export function useFetchInasistencias(dni: string | null) {
    const endpointUrl = import.meta.env.VITE_API_URL;
    const [inasistencias, setInasistencias] = useState<Inasistencia[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!dni) return;

        const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            // const response = await fetch(`${endpointUrl}/inasistencias`, {
            // method: "GET",
            // headers: {
            //     "Content-Type": "application/json",
            //     Authorization: `Bearer ${localStorage.getItem("token")}`,
            // },
            // body: JSON.stringify({ dni_usuario: dni }),
            // });
            const response = await fetch(`${endpointUrl}/inasistencias?dni=${dni}`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
                "Content-Type": "application/json",
            },
            });

            const data = await response.json();

            if (!response.ok) {
            throw new Error(data.error || "Error al cargar las inasistencias.");
            }

            // En caso de solo un mensaje
            if (data.message) {
            setInasistencias([]);
            } else {
            setInasistencias(data);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
        };

        fetchData();
    }, [dni]);

    return { inasistencias, loading, error };
    }