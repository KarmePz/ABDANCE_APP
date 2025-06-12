import { ReactNode } from 'react';
import { CuotaAdminTable, CuotaAlumnoTable } from '../CuotaTable';

interface Props{
    children?: ReactNode;
}

export function CuotaContentDashboard() {
  const usuario = JSON.parse(localStorage.getItem('usuario')|| '{}');
  return (
    <>
      <h1 className="tracking-wide text-4xl font-black text-gray-300 md:dark:text-gray-900">CUOTAS</h1>
      {usuario.rol === 'alumno' ? <CuotaAlumnoTable /> : <CuotaAdminTable />}
    </>
  );
}
export default CuotaContentDashboard;