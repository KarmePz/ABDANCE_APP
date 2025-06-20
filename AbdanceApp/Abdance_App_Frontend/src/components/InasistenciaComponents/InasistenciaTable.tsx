// src/components/Alumnos/InasistenciasTable.tsx
import { useAuth } from "../../hooks/useAuth";
import { /*Inasistencia,*/ useFetchInasistencias } from "../../hooks/useFetchInasistencias";

    type Props = {
    dni: string;
    nombre: string;
    apellido: string;
    onClose: () => void;
    };
    

    export function InasistenciasTable({ dni, nombre, apellido, onClose }: Props) {
    const { inasistencias, loading, error } = useFetchInasistencias(dni);
    const { user } = useAuth();  // <-- obtener usuario con rol desde el hook
    const esAlumno = user?.rol === "alumno";
    console.log("Es alumno? : " + esAlumno);
    
    
  return (
    <div className="p-4 bg-white rounded-lg shadow-lg">
      {!esAlumno && (
        <button
          onClick={onClose}
          className="mb-4 text-red-500 hover:underline"
        >
          ← Volver
        </button>
      )}

      <h2 className="text-xl font-semibold mb-2">Inasistencias de {nombre} {apellido}</h2>
      <p className="mb-2 text-sm text-gray-600">DNI: {dni}</p>

      {loading && <p>Cargando...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {inasistencias && inasistencias.length === 0 && <p>No tiene inasistencias registradas.</p>}

      {inasistencias && inasistencias.length > 0 && (
        <table className="w-full border mt-4 text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-4 py-2">Fecha</th>
              <th className="border px-4 py-2">Justificada</th>
            </tr>
          </thead>
          <tbody>
            {inasistencias.map((ina) => (
              <tr key={ina.id}>
                <td className="border px-4 py-2">{new Date(ina.fecha).toLocaleDateString()}</td>
                <td className="border px-4 py-2">{ina.justificada}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}