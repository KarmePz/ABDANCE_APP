import { useState } from 'react';

const monthNames = [
  'Enero','Febrero','Marzo','Abril','Mayo','Junio',
  'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'
];

const MONTH_ORDER = [
  "enero", "febrero", "marzo", "abril",
  "mayo", "junio", "julio", "agosto",
  "septiembre", "octubre", "noviembre", "diciembre"
];

export function EstadisticasTable() {
  const baseUrl = import.meta.env.VITE_API_URL;
  const token = localStorage.getItem('token');

  // 0 = ninguno, 1 = totales por año, 2 = total del mes
  const [mode, setMode] = useState<0|1|2>(0);

  // Common
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string|null>(null);

  // Form inputs
  const [year, setYear]   = useState<number>(new Date().getFullYear());
  const [month, setMonth] = useState<number>(new Date().getMonth()+1);

  // Responses
  const [byYearData, setByYearData] = useState<Record<string, number>|null>(null);
  const [byMonthData, setByMonthData] = useState<{
    Detalle: { fechaPago: string; montoPagado: number; concepto: string, DNIAlumno: number }[];
    Total: number;
  }|null>(null);

  const reset = () => {
    setError(null);
    setByYearData(null);
    setByMonthData(null);
  };

  const handleFetchByYear = async () => {
    reset();
    setLoading(true);
    try {
      const res = await fetch(`${baseUrl}/estadisticas/totales-por-anio`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type':  'application/json'
        },
        body: JSON.stringify({ year })
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      setByYearData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchByMonth = async () => {
    reset();
    setLoading(true);
    try {
      const res = await fetch(`${baseUrl}/estadisticas/total-del-mes`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type':  'application/json'
        },
        body: JSON.stringify({ year, month })
      });
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const json = await res.json();
      setByMonthData(json);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Modo */}
      <div className="space-x-2">
        <button
          className={`mx-1 mb-3 text-white px-4 py-2 rounded ${mode===1?'bg-blue-600 text-white':'bg-gray-200'}`}
          onClick={() => { reset(); setMode(1); }}
        >
          Ingresos Totales del año
        </button>
        <button
          className={`text-white px-4 py-2 rounded ${mode===2?'bg-blue-600 text-white':'bg-gray-200'}`}
          onClick={() => { reset(); setMode(2); }}
        >
          Ingresos Totales del mes
        </button>
      </div>

      {/* Formulario */}
      {mode !== 0 && (
        <div className="flex flex-wrap gap-4 items-center justify-center">
          <div>
            <p className="block text-sm font-medium">Año</p>
            <input
              type="number"
              className="mt-1 block w-24 rounded border-gray-300 p-1"
              value={year}
              onChange={e => setYear(Number(e.target.value))}
            />
          </div>
          {mode === 2 && (
            <div>
              <p className="block text-sm font-medium">Mes</p>
              <select
                className="mt-1 block rounded border-gray-300 p-1"
                value={month}
                onChange={e => setMonth(Number(e.target.value))}
              >
                {monthNames.map((m,n) =>
                  <option key={n+1} value={n+1}>{m}</option>
                )}
              </select>
            </div>
          )}
          <button
            className="px-4 py-2 bg-green-500 text-white rounded"
            onClick={mode===1? handleFetchByYear : handleFetchByMonth}
          >
            Consultar
          </button>
        </div>
      )}

      {/* Cargando/Error */}
      {loading && <p>Cargando...</p>}
      {error   && <p className="text-red-500">Error: {error}</p>}

      {/* Resultados */}
      {byYearData && (
         <table className="w-full table-auto border rounded">
            <thead>
            <tr className="bg-gray-100">
                <th className="p-2 text-gray-900">Mes</th>
                <th className="p-2 text-gray-900">Total</th>
            </tr>
            </thead>
            <tbody>
            {MONTH_ORDER.map(monthName => (
                <tr key={monthName} className="border-t">
                <td className="p-2 capitalize">{monthName}</td>
                <td className="p-2">
                    ${byYearData[monthName] ?? 0}
                </td>
                </tr>
            ))}
            </tbody>
        </table>
      )}

      {byMonthData && (
        <div className="space-y-2">
          <table className="w-full table-auto border rounded table-fixed">
            <thead><tr className="bg-gray-100">
              <th className="text-gray-900 p-2">Concepto</th>
              <th className="text-gray-900 p-2">Fecha Pago</th>
              <th className="text-gray-900 p-2">DNI de Alumno</th>
              <th className="text-gray-900 p-2">Monto</th>
            </tr></thead>
            <tbody>
              {byMonthData.Detalle.map((d,i) => (
                <tr key={i} className="border-t">
                  <td className='p-2'>{d.concepto}</td>
                  <td className="p-2">{new Date(d.fechaPago).toLocaleString()}</td>
                  <td className="p-2">{d.DNIAlumno}</td>
                  <td className="p-2">${d.montoPagado}</td>
                </tr>
              ))}
              <tr className="font-bold bg-gray-50">
                <td className="text-gray-900 p-2">Total</td>
                <td></td>
                <td></td>
                <td className="text-gray-900 p-2">${byMonthData.Total}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default EstadisticasTable