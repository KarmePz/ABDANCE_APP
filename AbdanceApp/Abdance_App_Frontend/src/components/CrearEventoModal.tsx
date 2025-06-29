import { useEffect, useState } from "react";
import InputField from "./InputField";
import axios from "axios";
import ImageManagerModal from "./ImageManagerModal";

// Define la interfaz para la estructura de un evento, similar a la de Eventos.tsx
interface Evento {
  codigo: string;
  nombre: string;
  lugar: string;
  fecha: any; // Puede ser un objeto Timestamp de Firebase o una cadena ISO
  urlImg: string;
  conEntrada: boolean;
  entradas?: Array<{ tipo: string; precio: string; cantidad: string }>;
  descripcion?: string;
}

// Define la interfaz para las props que recibirá CrearEventoModal
interface CrearEventoModalProps {
  onClose: () => void; // Función para cerrar el modal
  eventoExistente?: Evento | null; // El evento a editar, opcional y puede ser null
  onEventCreatedOrUpdated: () => void; // Callback para notificar al padre que se actualice la lista
}

export default function CrearEventoModal({
  onClose,
  eventoExistente, // Ahora correctamente tipado y recibido
  onEventCreatedOrUpdated, // Ahora correctamente tipado y recibido
}: CrearEventoModalProps) { // Usa la interfaz de props definida
  const [nombre, setNombre] = useState("");
  const [lugar, setLugar] = useState("");
  const [fecha, setFecha] = useState("");
  const [imagenUrl, setImagenUrl] = useState("");
  const [conEntrada, setConEntrada] = useState(true);
  const [descripcion, setDescripcion] = useState("");
  const endpointUrl = import.meta.env.VITE_API_URL_DEV;

  const [entradas, setEntradas] = useState([
    { tipo: "", precio: "", cantidad: "" },
  ]);

  // Estado para controlar la visibilidad del ImageManagerModal
  const [showImageManagerModal, setShowImageManagerModal] = useState(false);

  // useEffect para inicializar el formulario con los datos del evento existente si se proporcionan
  useEffect(() => {
    if (eventoExistente) {
      setNombre(eventoExistente.nombre);
      setLugar(eventoExistente.lugar);
      // Formatear la fecha para el campo de entrada (YYYY-MM-DD)
      // Asume que eventoExistente.fecha es un objeto Timestamp de Firebase
      const eventDate = new Date(eventoExistente.fecha.seconds * 1000);
      setFecha(eventDate.toISOString().split("T")[0]); // Obtiene solo la parte de la fecha (YYYY-MM-DD)
      setImagenUrl(eventoExistente.urlImg);
      setConEntrada(eventoExistente.conEntrada);
      if (eventoExistente.conEntrada && eventoExistente.entradas) {
        setEntradas(eventoExistente.entradas);
      } else if (eventoExistente.descripcion) {
        setDescripcion(eventoExistente.descripcion);
      }
    } else {
      // Si no hay evento existente, limpiar el formulario para un nuevo evento
      setNombre("");
      setLugar("");
      setFecha("");
      setImagenUrl("");
      setConEntrada(true);
      setDescripcion("");
      setEntradas([{ tipo: "", precio: "", cantidad: "" }]);
    }
  }, [eventoExistente]); // Se ejecuta cuando eventoExistente cambia

  // Función para manejar la URL de la imagen seleccionada desde el ImageManagerModal
  const handleImageSelect = (url: string) => {
    setImagenUrl(url);
    setShowImageManagerModal(false);
  };

  const agregarFila = () => {
    setEntradas([...entradas, { tipo: "", precio: "", cantidad: "" }]);
  };

  const eliminarFila = (index: number) => {
    if (entradas.length === 1) return; // No permitir eliminar la última fila
    setEntradas(entradas.filter((_, i) => i !== index));
  };

  const actualizarEntrada = (index: number, field: string, value: string) => {
    const nuevas = [...entradas];
    nuevas[index][field as keyof typeof nuevas[0]] = value;
    setEntradas(nuevas);
  };

  const enviarFormulario = async () => {
    // Validación básica de campos obligatorios
    if (
      !nombre ||
      !lugar ||
      !fecha ||
      !imagenUrl ||
      (conEntrada &&
        entradas.some((e) => !e.tipo || !e.precio || !e.cantidad)) || // Si es con entrada, validar campos de entrada
      (!conEntrada && !descripcion) // Si es sin entrada, validar descripción
    ) {
      alert("Por favor completá todos los campos obligatorios.");
      return;
    }

    // Preparar los datos del evento
    const data: Partial<Evento> = {
      nombre,
      lugar,
      fecha: new Date(fecha).toISOString(), // Enviar fecha en formato ISO para el backend
      urlImg: imagenUrl,
      conEntrada,
      ...(conEntrada ? { entradas } : { descripcion }), // Incluir entradas o descripción según el tipo de evento
    };

    try {
      if (eventoExistente) {
        // Si se está editando un evento existente, añade su código y envía una solicitud PUT
        data.codigo = eventoExistente.codigo; // Asegura que el código del evento se envía para la actualización
        await axios.put(`${endpointUrl}/eventos`, data);
        alert("Evento actualizado correctamente");
      } else {
        // De lo contrario, crea un nuevo evento con una solicitud POST
        await axios.post(`${endpointUrl}/eventos`, data);
        alert("Evento creado correctamente");
      }
      onClose(); // Cierra el modal después de la operación exitosa
      onEventCreatedOrUpdated(); // Llama al callback para que el componente padre refresque los eventos
    } catch (error) {
      console.error("Error al guardar evento:", error);
      alert("Error al guardar evento");
    }
  };

  return (
    // Agregamos 'p-4' o 'py-8' al contenedor principal para un padding vertical
    // También 'overflow-auto' para permitir el scroll si el contenido es demasiado grande
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 backdrop-blur-sm p-4 sm:p-8 overflow-auto">
      <div className="bg-white rounded-xl p-8 w-full max-w-2xl shadow-lg text-base sm:text-lg my-auto"> {/* Agregamos my-auto aquí */}
        <h2 className="text-xl font-bold mb-4 text-center text-[#1D094E]">
          {eventoExistente ? "Editar Evento" : "Crear Evento"} {/* Título dinámico */}
        </h2>

        <InputField label="Nombre del evento" value={nombre} onChange={setNombre} />
        <InputField label="Lugar" value={lugar} onChange={setLugar} />
        {/* Campo de fecha con tipo "date" */}
        <InputField label="Fecha" value={fecha} onChange={setFecha} type="date" />

        {/* Campo de imagen y botón para abrir el modal de gestión de imágenes */}
        <div className="mb-4">
          <InputField
            label="Imagen banner (URL)"
            value={imagenUrl}
            onChange={setImagenUrl}
            readOnly // Hacemos este campo de solo lectura para forzar el uso del gestor de imágenes
            placeholder="Selecciona una imagen desde el gestor"
          />
          <button
            type="button"
            onClick={() => setShowImageManagerModal(true)}
            className="mt-2 bg-[#1D094E] text-white px-4 py-2 rounded-full hover:bg-[#2a136e] transition-colors"
          >
            Seleccionar/Subir Imagen
          </button>
        </div>

        {/* Opciones de "Con entradas" / "Sin entradas" */}
        <div className="flex gap-6 mt-4 mb-6 items-center text-[#1D094E]">
          <label className="flex items-center gap-2 text-base">
            <input
              type="radio"
              name="entrada"
              checked={conEntrada}
              onChange={() => setConEntrada(true)}
              className="accent-[#1D094E] w-4 h-4"
            />{" "}
            Con entradas
          </label>
          <label className="flex items-center gap-2 text-base">
            <input
              type="radio"
              name="entrada"
              checked={!conEntrada}
              onChange={() => setConEntrada(false)}
              className="accent-[#1D094E] w-4 h-4"
            />{" "}
            Sin entradas
          </label>
        </div>

        {/* Sección de entradas o descripción, condicional según 'conEntrada' */}
        {conEntrada ? (
          <div className="space-y-3">
            {entradas.map((entrada, i) => (
              <div key={i} className="flex items-end gap-2 w-full">
                <div className="w-2/7">
                  <InputField
                    label="Tipo"
                    value={entrada.tipo}
                    onChange={(val) => actualizarEntrada(i, "tipo", val)}
                    // Clases de estilo para el InputField
                    className="w-full text-lg rounded-full bg-[#1D094E] text-white px-4 py-2"
                  />
                </div>
                <div className="w-2/7">
                  <InputField
                    label="Precio"
                    value={entrada.precio}
                    onChange={(val) => actualizarEntrada(i, "precio", val)}
                    className="w-full text-lg rounded-full bg-[#1D094E] text-white px-4 py-2"
                  />
                </div>
                <div className="w-2/7">
                  <InputField
                    label="Cantidad"
                    value={entrada.cantidad}
                    onChange={(val) => actualizarEntrada(i, "cantidad", val)}
                    className="w-full text-lg rounded-full bg-[#1D094E] text-white px-4 py-2"
                  />
                </div>
                {/* Botones para agregar/eliminar filas de entrada */}
                <div className="w-1/7 flex flex-col items-center gap-1">
                  <button
                    className="bg-[#1D094E] border border-[#1D094E] rounded-full w-10 h-10 flex items-center justify-center text-2xl font-bold text-white"
                    onClick={() => agregarFila()}
                  >
                    +
                  </button>
                  <button
                    className="bg-[#1D094E] border border-[#1D094E] rounded-full w-10 h-10 flex items-center justify-center text-2xl font-bold text-white"
                    onClick={() => eliminarFila(i)}
                  >
                    -
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Campo de descripción si el evento es sin entradas
          <InputField
            label="Descripción del evento"
            value={descripcion}
            onChange={setDescripcion}
          />
        )}
        <div className="flex justify-end gap-4 mt-6">
          {/* Botón Cancelar */}
          <button
            onClick={onClose}
            className="rounded-full px-4 py-2 font-semibold"
          >
            Cancelar
          </button>
          {/* Botón Confirmar/Guardar Cambios (texto dinámico) */}
          <button
            onClick={enviarFormulario}
            className="rounded-full px-6 py-2 font-semibold bg-[#1D094E] text-white hover:bg-[#2a136e] transition-colors"
          >
            {eventoExistente ? "Guardar Cambios" : "Confirmar"}
          </button>
        </div>
      </div>

      {/* Renderiza el ImageManagerModal condicionalmente */}
      {showImageManagerModal && (
        <ImageManagerModal
          onClose={() => setShowImageManagerModal(false)}
          onSelectImage={handleImageSelect}
        />
      )}
    </div>
  );
}