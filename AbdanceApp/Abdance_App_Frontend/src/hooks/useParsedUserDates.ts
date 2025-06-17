    import { useState, useEffect } from "react";

    type User = {
        dni: string;
        nombre: string;
        apellido: string;
        email: string;
        rol: string;
        fechaNacimiento?: string | null;
        fechaInscripcion?: string | null;
        nombreAcceso?: string;
        user_uid?: string;
        };

    function parseDateToISO(dateString?: string | null): string | null {
    if (!dateString) return null;
    const date = new Date(dateString);
    // Asegurarse que la fecha es válida
    if (isNaN(date.getTime())) return null;
    // Devuelve el string ISO 8601 sin la Z final (que indica UTC)
    return date.toISOString().slice(0, 19);
    }

    export function useParsedUserDates(user : User | null) {
    const [parsedUser, setParsedUser] = useState({ ...user });

    useEffect(() => {
        if (!user) return;
        setParsedUser({
        ...user,
        fechaNacimiento: parseDateToISO(user.fechaNacimiento),
        fechaInscripcion: parseDateToISO(user.fechaInscripcion),
        });
    }, [user]);

    return parsedUser;
    }