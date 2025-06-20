import { useEffect, useState } from "react";
import { SelectEventosConEntradas } from "../components/SelectEventosConEntradas";
import { FaSearch, FaInfoCircle, FaCheckCircle, FaExpand  } from "react-icons/fa";
import ValidarEntradaModal from "../components/ValidarEntradaModal";
import { useNavigate } from 'react-router-dom';


interface Entrada {
  id: string;
  nombre: string;
  apellido: string;
  dni: string;
  email: string;
  telefono: string;
  tipo_entrada: string;
  estado: string;
  created_at: string;
}

export const EntradasDashboard = () => {
  const [eventoSeleccionado, setEventoSeleccionado] = useState<string>("");
  const [entradas, setEntradas] = useState<Entrada[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [entradaSeleccionada, setEntradaSeleccionada] = useState<Entrada | null>(null);
  const [entradaAValidar, setEntradaAValidar] = useState<Entrada | null>(null);
  const navigate = useNavigate();
  // Cargar entradas cuando cambia el evento
  useEffect(() => {
    if (!eventoSeleccionado) return;

    fetch(`http://localhost:5000/entradas?evento_id=${eventoSeleccionado}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setEntradas(data);
        } else {
          console.error("Error al obtener entradas:", data);
          setEntradas([]);
        }
      })
      .catch((err) => {
        console.error("Error en fetch de entradas:", err);
        setEntradas([]);
      });
  }, [eventoSeleccionado]);

  const filtradas = entradas.filter((e) => {
    const texto = `${e.nombre} ${e.apellido} ${e.dni} ${e.email}`.toLowerCase();
    return texto.includes(busqueda.toLowerCase());
  });

  const validarEntrada = async () => {
    if (!entradaAValidar || !eventoSeleccionado) return;

    const response = await fetch("http://localhost:5000/entradas", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        evento_id: eventoSeleccionado,
        entrada_id: entradaAValidar.id,
        estado: "validada",
      }),
    });

    if (response.ok) {
      // Actualizar el estado localmente
      setEntradas((prev) =>
        prev.map((e) =>
          e.id === entradaAValidar.id ? { ...e, estado: "validada" } : e
        )
      );
    }

    setEntradaAValidar(null);
  };

  return (
    <div className="w-full max-w-md mx-auto mt-6 relative text-center">
      <SelectEventosConEntradas
        onSelect={(eventoId) => {
          setEventoSeleccionado(eventoId);
          localStorage.setItem("evento_seleccionado", eventoId); // <- GUARDA EN LOCAL
        }}
      />
      
      {eventoSeleccionado && (
        <>
          <div className="w-full max-w-md mx-auto mt-6 relative">
            <input
              type="text"
              placeholder="Buscar Entrada"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-5 pr-10 py-3 rounded-full bg-white placeholder:font-bold text-[#1D094E] font-bold focus:outline-none shadow-md"
            />
            <FaSearch className="absolute right-4 top-1/2 transform -translate-y-1/2 text-[#3299D9] text-2xl" />
          </div>
          <h2 className="text-black text-center mt-2 text-sm font-bold">
            Buscar por <strong>Nombre, Email, DNI.</strong>
          </h2>
        </>
      )}

      <ul className="mt-4 space-y-3">
        {filtradas.map((entrada) => (
          <li
            key={entrada.id}
            className="bg-white p-4 rounded-xl shadow flex items-center justify-between text-left"
          >
            <div className="text-[#1D094E] font-semibold">
              {entrada.nombre} {entrada.apellido} - {entrada.dni}
              <span className="text-sm text-gray-500"> ({entrada.tipo_entrada})</span>
            </div>

            <div className="flex items-center space-x-3">
              {/* Botón Info */}
              <button onClick={() => setEntradaSeleccionada(entrada)} title="Ver detalles">
                <FaInfoCircle className="text-yellow-500 text-xl" />
              </button>

              {/* Icono Validar */}
              <FaCheckCircle
                onClick={() => {
                  if (entrada.estado === "activa") {
                    setEntradaAValidar(entrada);
                  }
                }}
                className={`cursor-pointer text-xl ${
                  entrada.estado === "validada"
                    ? "text-green-500"
                    : "text-white border border-gray-300"
                }`}
              />
            </div>
          </li>
        ))}
      </ul>

      {/* Modal para Info general */}
      {entradaSeleccionada && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
          <div className="bg-white rounded-xl shadow-lg p-6 w-11/12 max-w-md">
            <h3 className="text-lg font-bold text-[#1D094E] mb-4">Detalle de Entrada</h3>
            <ul className="text-left space-y-2">
              <li><strong>Nombre:</strong> {entradaSeleccionada.nombre} {entradaSeleccionada.apellido}</li>
              <li><strong>DNI:</strong> {entradaSeleccionada.dni}</li>
              <li><strong>Email:</strong> {entradaSeleccionada.email}</li>
              <li><strong>Teléfono:</strong> {entradaSeleccionada.telefono}</li>
              <li><strong>Tipo de Entrada:</strong> {entradaSeleccionada.tipo_entrada}</li>
              <li><strong>Estado:</strong> {entradaSeleccionada.estado}</li>
              <li><strong>Fecha de creación:</strong> {entradaSeleccionada.created_at}</li>
            </ul>
            <button
              className="mt-4 px-4 py-2 bg-[#1D094E] text-white rounded-full hover:bg-[#3a248d]"
              onClick={() => setEntradaSeleccionada(null)}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Modal para validar entrada */}
      {entradaAValidar && (
        <ValidarEntradaModal
          entrada={entradaAValidar}
          onClose={() => setEntradaAValidar(null)}
          onValidar={validarEntrada}
        />
      )}
      <div className="flex justify-center gap-6 mt-6">
        <button className="text-cyan-400 text-3xl">
          <FaSearch />
        </button>
        <button
          className="text-white text-3xl"
          onClick={() => navigate("/dashboard/escanear")}
        >
          <FaExpand />
        </button>
      </div>



    </div>
    
  );
};

export default EntradasDashboard;
