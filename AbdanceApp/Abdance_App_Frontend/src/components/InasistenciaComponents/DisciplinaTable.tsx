import { useAuthFetch } from "../../hooks/useAuthFetch";

type Disciplina = {
    disciplina_id: string;
    nombre: string;
    edadMinima: number;
    edadMaxima: number;
    alumnos_inscriptos: any[]; // lista, pero usaremos solo su longitud
    precios: {
        matriculaAnual: number;
        montoBase: number;
        montoNuevo15: number;
        montoRecargo: number;
    };
};

export function DisciplinaTable() {
    const endpointUrl = import.meta.env.VITE_API_URL;
    const { data: disciplinas, loading, error } = useAuthFetch<Disciplina[]>(`${endpointUrl}/disciplinas`);

    if (loading) return <p className="text-gray-500">Cargando disciplinas...</p>;
    if (error) return <p className="text-red-500">Error: {error}</p>;
    if (!disciplinas || disciplinas.length === 0) return <p>No hay disciplinas registradas.</p>;

    return (
        <table className="min-w-full table-auto border border-gray-200 shadow-sm rounded-md">
            <thead className="bg-gray-100">
                <tr>
                    <th className="px-4 py-2 text-center">Nombre</th>
                    <th className="px-4 py-2 text-center">Edad Mínima</th>
                    <th className="px-4 py-2 text-center">Edad Máxima</th>
                    <th className="px-4 py-2 text-center">Inscriptos</th>
                    <th className="px-4 py-2 text-center">Matrícula</th>
                    <th className="px-4 py-2 text-center">Monto Base</th>
                    <th className="px-4 py-2 text-center">Monto Nuevo (15)</th>
                    <th className="px-4 py-2 text-center">Recargo</th>
                    <th className="px-4 py-2 text-center">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {disciplinas.map((disc) => (
                    <tr key={disc.disciplina_id} className="border-t text-center">
                        <td className="px-4 py-2">{disc.nombre}</td>
                        <td className="px-4 py-2">{disc.edadMinima}</td>
                        <td className="px-4 py-2">{disc.edadMaxima}</td>
                        <td className="px-4 py-2">{disc.alumnos_inscriptos.length}</td>
                        <td className="px-4 py-2">${disc.precios.matriculaAnual}</td>
                        <td className="px-4 py-2">${disc.precios.montoBase}</td>
                        <td className="px-4 py-2">${disc.precios.montoNuevo15}</td>
                        <td className="px-4 py-2">${disc.precios.montoRecargo}</td>
                        <td className="px-4 py-2 space-x-2">
                            <button
                                className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                                // onClick={() => handleEdit(disc.disciplina_id)}
                            >
                                Editar
                            </button>
                            <button
                                className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                                // onClick={() => handleDelete(disc.disciplina_id)}
                            >
                                Eliminar
                            </button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}