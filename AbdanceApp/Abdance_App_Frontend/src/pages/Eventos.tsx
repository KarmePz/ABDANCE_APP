import { useEffect, useState } from "react";
import { db } from "../firebase-config";
import { collection, getDocs } from "firebase/firestore";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import NeonButton from "../components/NeonButton";
import CrearEventoModal from "../components/CrearEventoModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal"; // Importa el nuevo modal de confirmación
import { FaPencilAlt, FaTrashAlt } from 'react-icons/fa';
import axios from "axios";

// Define la interfaz para la estructura de un evento
interface Evento {
  codigo: string;
  nombre: string;
  lugar: string;
  fecha: any;
  urlImg: string;
  conEntrada: boolean;
  entradas?: Array<{ tipo: string; precio: string; cantidad: string }>;
  descripcion?: string;
}

const Eventos = () => {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [mostrarCrearEditarModal, setMostrarCrearEditarModal] = useState(false); // Renombrado para claridad
  const [eventoParaEditar, setEventoParaEditar] = useState<Evento | null>(null);

  // Nuevo estado para el modal de confirmación de eliminación
  const [mostrarConfirmDeleteModal, setMostrarConfirmDeleteModal] = useState(false);
  const [eventoCodigoAEliminar, setEventoCodigoAEliminar] = useState<string | null>(null);

  const endpointUrl = import.meta.env.VITE_API_URL_DEV;

  const fetchEventos = async () => {
    try {
      const querySnapshot = await getDocs(collection(db, "eventos"));
      const eventosData: Evento[] = querySnapshot.docs.map((document) => {
        const data = document.data();
        return {
          ...data,
          codigo: data.codigo || document.id,
        } as Evento;
      });
      setEventos(eventosData);
    } catch (error) {
      console.error("Error al cargar eventos:", error);
    }
  };

  useEffect(() => {
    fetchEventos();
  }, []);

  // Efecto para controlar la clase 'modal-abierto' en el body
  useEffect(() => {
    if (mostrarCrearEditarModal || mostrarConfirmDeleteModal) { // Ahora considera ambos modales
      document.body.classList.add("modal-abierto");
    } else {
      document.body.classList.remove("modal-abierto");
      setEventoParaEditar(null);
      setEventoCodigoAEliminar(null); // Limpiar también el código a eliminar
    }

    return () => {
      document.body.classList.remove("modal-abierto");
    };
  }, [mostrarCrearEditarModal, mostrarConfirmDeleteModal]); // Depende de ambos estados de modal

  const handleEdit = (evento: Evento) => {
    setEventoParaEditar(evento);
    setMostrarCrearEditarModal(true);
  };

  // Función que se llama cuando se hace clic en el ícono de papelera
  const handleRequestDelete = (codigo: string) => {
    setEventoCodigoAEliminar(codigo); // Guarda el código del evento a eliminar
    setMostrarConfirmDeleteModal(true); // Abre el modal de confirmación
  };

  // Función que se llama si el usuario CONFIRMA la eliminación en el modal
  const handleConfirmDelete = async () => {
    if (eventoCodigoAEliminar) {
      try {
        await axios.delete(`${endpointUrl}/eventos`, { data: { codigo: eventoCodigoAEliminar } });
        alert("Evento eliminado correctamente");
        fetchEventos(); // Refrescar eventos después de la eliminación
      } catch (error) {
        console.error("Error al eliminar evento:", error);
        alert("Error al eliminar evento");
      } finally {
        setMostrarConfirmDeleteModal(false); // Cierra el modal de confirmación
        setEventoCodigoAEliminar(null); // Limpia el código
      }
    }
  };

  // Función que se llama si el usuario CANCELA la eliminación en el modal
  const handleCancelDelete = () => {
    setMostrarConfirmDeleteModal(false); // Cierra el modal de confirmación
    setEventoCodigoAEliminar(null); // Limpia el código
  };

  if (loading) return <p className="text-center text-white">Cargando...</p>;

  return (
    <div
      className={` ${
        (mostrarCrearEditarModal || mostrarConfirmDeleteModal) ? "backdrop-blur-sm transition-all duration-300" : ""
      }`}
    >
      <div className="p-6 text-white">
        <h1 className="text-2xl font-bold mb-6 text-center">Eventos</h1>

        {user?.rol === "admin" && (
          <div className="flex justify-center mb-6">
            <NeonButton onClick={() => setMostrarCrearEditarModal(true)}>
              Agregar Evento
            </NeonButton>
          </div>
        )}

        {mostrarCrearEditarModal && (
          <>
            <div className="blur-overlay"></div>
            <CrearEventoModal
              onClose={() => setMostrarCrearEditarModal(false)}
              eventoExistente={eventoParaEditar}
              onEventCreatedOrUpdated={fetchEventos}
            />
          </>
        )}

        {/* Renderiza el ConfirmDeleteModal condicionalmente */}
        {mostrarConfirmDeleteModal && (
          <ConfirmDeleteModal
            onConfirm={handleConfirmDelete}
            onCancel={handleCancelDelete}
          />
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {eventos.map((evento) => (
            <div
              key={evento.codigo}
              className="hover:scale-105 transition transform bg-white/10 backdrop-blur-md p-4 rounded-lg shadow-md"
            >
              <div onClick={() => navigate(`/evento/${evento.codigo}`)}>
                <img
                  src={evento.urlImg}
                  alt={evento.nombre}
                  className="w-full h-48 object-cover mb-4 rounded-lg"
                />
                <h2 className="text-xl font-semibold">{evento.nombre}</h2>
                <p className="text-sm text-white/80">
                  {new Date(evento.fecha.seconds * 1000).toLocaleDateString()}
                </p>
                <p className="text-sm text-white/80">{evento.lugar}</p>
              </div>

              {user?.rol === "admin" && (
                <div className="flex justify-end gap-3 mt-4">
                  <FaTrashAlt
                    className="h-5 w-5 text-red-500 cursor-pointer hover:text-red-600"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRequestDelete(evento.codigo); // Llama a la nueva función
                    }}
                  />
                  <FaPencilAlt
                    className="h-5 w-5 text-yellow-400 cursor-pointer hover:text-yellow-500"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(evento);
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Eventos;