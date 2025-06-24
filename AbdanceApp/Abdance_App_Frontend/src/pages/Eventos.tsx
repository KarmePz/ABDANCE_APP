import { useEffect, useState } from "react";
import { db } from "../firebase-config";
import { collection, getDocs } from "firebase/firestore";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth"; 
import NeonButton from "../components/NeonButton"; 
import CrearEventoModal from "../components/CrearEventoModal";

interface Evento {
  codigo: string;
  nombre: string;
  lugar: string;
  fecha: any;
  urlImg: string;
}

const Eventos = () => {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [mostrarModal, setMostrarModal] = useState(false);

  useEffect(() => {
    const fetchEventos = async () => {
      try {
        const querySnapshot = await getDocs(collection(db, "eventos"));
        const eventosData: Evento[] = querySnapshot.docs.map((doc) => ({
          ...doc.data(),
          codigo: doc.data().codigo || doc.id,
        })) as Evento[];
        setEventos(eventosData);
      } catch (error) {
        console.error("Error al cargar eventos:", error);
      }
    };

    fetchEventos();
  }, []);

  if (loading) return <p className="text-center text-white">Cargando...</p>;

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl font-bold mb-6 text-center">Eventos</h1>

      {/* Botón Agregar Evento solo para admins */}
      {user?.rol === "admin" && (
        <div className="flex justify-center mb-6">
          <NeonButton onClick={() => setMostrarModal(true)}>
            Agregar Evento
          </NeonButton>
        </div>
      )}

      {mostrarModal && (
        <CrearEventoModal onClose={() => setMostrarModal(false)} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {eventos.map((evento) => (
          <div
            key={evento.codigo}
            onClick={() => navigate(`/evento/${evento.codigo}`)}
            className="cursor-pointer hover:scale-105 transition transform bg-white/10 backdrop-blur-md p-4 rounded-lg shadow-md"
          >
            <img
              src={evento.urlImg}
              alt={evento.nombre}
              className="w-full h-48 object-cover mb-4 rounded-lg"
            />
            <h2 className="text-xl font-semibold">{evento.nombre}</h2>
            <p className="text-sm text-white/80">{evento.lugar}</p>
            <p className="text-sm text-white/80">
              {new Date(evento.fecha.seconds * 1000).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Eventos;
