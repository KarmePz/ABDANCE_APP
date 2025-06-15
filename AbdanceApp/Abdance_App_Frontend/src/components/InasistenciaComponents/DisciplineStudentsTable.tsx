import { useEffect, useState } from "react";
import { useAuthFetch } from "../../hooks/useAuthFetch";
import { Loader } from "..";

type Student = {
    dni: string;
    nombre: string;
    apellido: string;
    email: string;
    rol: string;
};

export function DisciplineStudentsTable({
    disciplinaId,
    reloadFlag,
    onUserUpdated,
}: {
    disciplinaId: string;
    reloadFlag: number;
    onUserUpdated: () => void;
}) {
    const endpointUrl = import.meta.env.VITE_API_URL;
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [nombreDisciplina, setNombreDisciplina] = useState("");

    useEffect(() => {
        const fetchStudents = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${endpointUrl}/disciplinas?disciplina_id=${disciplinaId}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            // body: JSON.stringify({ disciplina_id: disciplinaId }),
            });

            const data = await res.json();
            setStudents(data.alumnos_inscriptos);
            setNombreDisciplina(data.nombre);
        } catch (error) {
            console.error("Error cargando alumnos:", error);
        } finally {
            setLoading(false);
        }
        };

        fetchStudents();
    }, [disciplinaId, reloadFlag]);

    const registrarInasistencia = async (dni: string) => {
        const confirm = window.confirm(`¿Registrar inasistencia para DNI ${dni}?`);
        if (!confirm) return;

        try {
        const res = await fetch(`${endpointUrl}/asistencias/registrar`, {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            body: JSON.stringify({
            dni_usuario: dni,
            justificada: "NO", // o true si querés marcarla justificada
            }),
        });

        const result = await res.json();
        alert(result.message || "Inasistencia registrada");
        onUserUpdated();
        } catch (error) {
        alert("Error registrando la inasistencia");
        }
    };

    if (loading)
        return (
        <div className="flex justify-center items-center w-full h-full">
            <Loader />
        </div>
        );

    const tableHeaderStyle = "bg-[#fff0] text-white";
    const tableCellStyle = "bg-white text-blue-600 rounded-xl m-0.5 p-1";

    return (
        <div className="w-full overflow-x-auto">
            <h1>Disciplina: {nombreDisciplina}</h1>
        <div className="min-w-[640px] mx-auto">
            <table className="table-fixed min-w-[99%] border-spacing-2 border-separate border bg-[#1a0049] rounded-xl">
            <thead>
                <tr>
                <th className={tableHeaderStyle}>DNI</th>
                <th className={tableHeaderStyle}>Nombre</th>
                <th className={tableHeaderStyle}>Apellido</th>
                <th className={tableHeaderStyle}>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {students.map((student) => (
                <tr key={student.dni}>
                    <td className={tableCellStyle}>{student.dni}</td>
                    <td className={tableCellStyle}>{student.nombre}</td>
                    <td className={tableCellStyle}>{student.apellido}</td>
                    <td className="text-center">
                    <button
                        className="bg-red-500 text-white rounded px-2 py-1 hover:bg-red-700"
                        onClick={() => registrarInasistencia(student.dni)}
                    >
                        Marcar Falta
                    </button>
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
        </div>
    );
}
