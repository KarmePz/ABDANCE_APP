import { useState } from "react";
import { useAuthFetch } from "../hooks/useAuthFetch";
import { Dialog, DialogTitle } from "@headlessui/react";

type Cuota = {
    concepto: string;
    dniAlumno: string;
    estado: string;
    fechaPago: string;
    id: string;
    idDisciplina: string;
    metodoPago: string;
    precio_cuota: string;
};

//Ventada de tipo modal para pagar las cuotas seleccionadas.
export function PagoManualModal({open, onClose, selectedCuotas, onSuccess, }: {
    open: boolean;
    onClose: () => void;
    selectedCuotas: Cuota[];
    onSuccess: () => void;
    }) {
  const [loading, setLoading] = useState(false);

  //Endpoint para pagar las cuotas seleccionadas
  const token = localStorage.getItem("token");
  const endpointUrl = import.meta.env.VITE_API_URL;
  const handleConfirm = async () => {
    setLoading(true);
    const listaIds = selectedCuotas.map(c => c.id);

    try {
      /* const res = await fetch(
        `${endpointUrl}/pagar_cuota/manual?dia_recargo=11`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ lista_cuotas: listaIds }),
        }
      ); */
      const res = await fetch(
        `http://192.168.0.194:8080/pagar_cuota/manual?dia_recargo=11`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ lista_cuotas: listaIds }),
        }
      );
      if (!res.ok) throw new Error("Error en el pago manual");
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="bg-indigo-200 p-6 rounded-lg shadow-lg max-w-md w-full text-black">
        <DialogTitle className="text-xl font-extrabold mb-4 text-center">Confirmar Pago Manual</DialogTitle>
        <div className="space-y-2 max-h-60 overflow-auto mb-8">
          {selectedCuotas.map(c => (
            <div key={c.id} className=""> 
              <ul className="list-inside list-disc"><em><strong>ID de Cuota: </strong></em>{c.id}
                <li><b>DNI Alumno: </b>{c.dniAlumno}</li>
                <li>Concepto: {c.concepto}</li>
                <li>Concepto: {c.precio_cuota}</li>
              </ul>
              {/* <span>{c.concepto}</span>
              <span>{c.precio_cuota}</span>
              <span><strong>DNI Alumno: </strong>{c.dniAlumno}</span> */}
            </div>
          ))}
        </div>
        <p className="text-sm text-black text-center italic mb-3">Las fechas de pago quedarán con la fecha y hora actual</p>
        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-white rounded hover:bg-gray-300"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            disabled={loading}
          >
            {loading ? 'Procesando...' : 'Confirmar'}
          </button>
        </div>
      </div>
    </Dialog>
  );
}


//Componente de la tabla de cuotas
export function CuotaTable() {
  const endpointUrl = import.meta.env.VITE_API_URL;
  const [reloadFlag, setReloadFlag] = useState(0);
  /* const { data: cuotas, loading, error } = useAuthFetch<Cuota[]>(
    `${endpointUrl}/cuotas?dia_recargo=11&reload=${reloadFlag}`
  ); */
  const { data: cuotas, loading, error } = useAuthFetch<Cuota[]>(
    `http://192.168.0.194:8080/cuotas?dia_recargo=11&reload=${reloadFlag}`);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [open, setOpen] = useState(false);

  //Construye la lista de cuotas seleccionadas
  const selectedCuotas = cuotas?.filter(c => selectedIds.has(c.id)) || [];

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const openModal = () => {
    if (selectedIds.size === 0) return;
    setOpen(true);
  };

  const handleClose = () => setOpen(false);
  const handleSuccess = () => setReloadFlag(prev => prev + 1);

  if (loading) return <p>Cargando...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <>
      <table className="min-w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th></th>
            <th>Concepto</th>
            <th>DNI Alumno</th>
            <th>Estado</th>
            <th>Fecha de Pago</th>
            <th>Disciplina</th>
            <th>Metodo de Pago</th>
            <th>Cantidad</th>
          </tr>
        </thead>
        <tbody>
          {cuotas?.map(c => (
            <tr key={c.id} className={selectedIds.has(c.id) ? 'bg-yellow-50' : ''}>
              <td className="p-2">
                <input
                  type="checkbox"
                  checked={selectedIds.has(c.id)}
                  onChange={() => toggleSelect(c.id)}
                />
              </td>
              <td>{c.concepto}</td>
              <td>{c.dniAlumno}</td>
              <td>{c.estado}</td>
              <td>{c.fechaPago}</td>
              <td>{c.idDisciplina}</td>
              <td>{c.metodoPago}</td>
              <td>{c.precio_cuota}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <button
        onClick={openModal}
        disabled={selectedIds.size === 0}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        Pagar Seleccionadas
      </button>

      <PagoManualModal
        open={open}
        onClose={handleClose}
        selectedCuotas={selectedCuotas}
        onSuccess={handleSuccess}
      />
    </>
  );
}




/* export function CuotaTable() {
    const endpointUrl =  import.meta.env.VITE_API_URL
    const [reloadFlag, setReloadFlag] = useState(0); //controla los cambios de la tabla

    const { data: users, loading, error } = useAuthFetch<Cuota[]>(`${endpointUrl}/cuotas?dia_recargo=28&reload=${reloadFlag}`);
    const [selectedCuota, setSelectedCuota] = useState<Cuota | null>(null);
    const [open, setOpen] = useState(false);

    const handleEdit = (cuota: Cuota) => {
        setSelectedCuota(cuota);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setSelectedCuota(null);
    };
    
    // Esta función se pasa para forzar recarga
    const handleCuotaUpdated = () => {
        setReloadFlag((prev) => prev + 1);
    };

    if (loading) return <p>Cargando...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <>
        <table className="min-w-full border">
            <thead>
            <tr className="bg-gray-200">
                <th>Concepto</th>
                <th>DNI Alumno</th>
                <th>Estado</th>
                <th>Fecha de Pago</th>
                <th>Disciplina</th>
                <th>Metodo de Pago</th>
                <th>Cantidad a Pagar/Pagada</th>
                <th>Acciones</th>
            </tr>
            </thead>
            <tbody>
            {users?.map((cuota) => (
                <tr key={cuota.concepto}>
                <td>{cuota.dniAlumno}</td>
                <td>{cuota.estado}</td>
                <td>{cuota.fechaPago}</td>
                <td>{cuota.idDisciplina}</td>
                <td>{cuota.metodoPago}</td>
                <td>{cuota.precioCuota}</td>
                <td>
                    <button
                    className="bg-blue-500 text-white px-2 py-1 rounded mr-2"
                    onClick={() => handleEdit(cuota)}
                    >
                    Pagar
                    </button>
                </td>
                </tr>
            ))}
            </tbody>
        </table>

         {selectedCuota && (
            <PagoManualForm open={open} cuota={selectedCuota} onClose={handleClose} onCuotaUpdated={handleCuotaUpdated} />
        )} 
        </>
    );
} 
*/