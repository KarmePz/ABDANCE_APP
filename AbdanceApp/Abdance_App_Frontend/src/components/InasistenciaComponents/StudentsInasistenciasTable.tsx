    import { useState } from "react";
    import { useAuthFetch } from "../../hooks/useAuthFetch";
    import { Loader } from "..";
    import { InasistenciasTable } from "./InasistenciaTable"; // Asegúrate de tener este componente

    type User = {
    id: string;
    dni: string;
    nombre: string;
    apellido: string;
    email: string;
    rol: string;
    };

    export function StudentsInasistenciasTable({ reloadFlag }: { reloadFlag: number }) {
    const endpointUrl = import.meta.env.VITE_API_URL;

    const { data: users, loading, error } = useAuthFetch<User[]>(
        `${endpointUrl}/usuarios?reload=${reloadFlag}`
    );

    const [alumnoParaFaltas, setAlumnoParaFaltas] = useState<User | null>(null);

    // Solo mostrar alumnos
    const alumnos = users?.filter((user) => user.rol === "alumno");

    const tableHeaderStyle = "bg-[#fff0] text-[#fff] justify-center";
    const tableDatacellStyle = "text-blue-500 bg-white rounded-xl m-0.5 p-1";

    if (loading)
        return (
        <div className="flex justify-center align-middle items-center w-full h-full">
            <Loader />
        </div>
        );

    if (error) return <p>Error: {error}</p>;

    if (alumnoParaFaltas) {
        return (
        <InasistenciasTable
            dni={alumnoParaFaltas.dni}
            nombre={alumnoParaFaltas.nombre}
            apellido={alumnoParaFaltas.apellido}
            onClose={() => setAlumnoParaFaltas(null)}
        />
        );
    }

    return (
        <div className="w-full overflow-x-auto">
        <div className="min-w-[640px] mx-auto">
            <table className="table-fixed min-w-[99%] rounded-xl border-none md:border m-1 bg-transparent md:bg-[#1a0049] border-separate border-spacing-x-1 border-spacing-y-1 w-auto">
            <thead>
                <tr className="bg-transparent">
                <th className={tableHeaderStyle + " w-[100px]"}>DNI</th>
                <th className={tableHeaderStyle + " w-[120px]"}>Nombre</th>
                <th className={tableHeaderStyle + " w-[120px]"}>Apellido</th>
                <th className="bg-[#fff0] text-[#fff] w-[80px]">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {alumnos?.map((user) => (
                <tr key={user.dni}>
                    <td className={`${tableDatacellStyle} truncate max-w-[100px]`}>
                    {user.dni}
                    </td>
                    <td className={`${tableDatacellStyle} truncate max-w-[120px]`}>
                    {user.nombre}
                    </td>
                    <td className={`${tableDatacellStyle} truncate max-w-[120px]`}>
                    {user.apellido}
                    </td>
                    <td className="w-[80px]">
                    <button
                        onClick={() => setAlumnoParaFaltas(user)}
                        className="text-blue-600 underline"
                    >
                        Ver faltas
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