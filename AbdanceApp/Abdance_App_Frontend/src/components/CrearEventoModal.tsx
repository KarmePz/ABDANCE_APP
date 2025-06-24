import { useState } from "react";
import InputField from "./InputField";
import NeonButton from "./NeonButton";
import SimpleButton from "./SimpleButton";
import axios from "axios";

export default function CrearEventoModal({ onClose }: { onClose: () => void }) {
  const [nombre, setNombre] = useState("");
  const [lugar, setLugar] = useState("");
  const [fecha, setFecha] = useState("");
  const [imagenUrl, setImagenUrl] = useState("");
  const [conEntrada, setConEntrada] = useState(true);
  const [descripcion, setDescripcion] = useState("");

  const [entradas, setEntradas] = useState([
    { tipo: "", precio: "", cantidad: "" },
  ]);

  const agregarFila = () => {
    setEntradas([...entradas, { tipo: "", precio: "", cantidad: "" }]);
  };

  const eliminarFila = (index: number) => {
    if (entradas.length === 1) return;
    setEntradas(entradas.filter((_, i) => i !== index));
  };

  const actualizarEntrada = (index: number, field: string, value: string) => {
    const nuevas = [...entradas];
    nuevas[index][field as keyof typeof nuevas[0]] = value;
    setEntradas(nuevas);
  };

  const enviarFormulario = async () => {
    if (!nombre || !lugar || !fecha || !imagenUrl || (conEntrada && entradas.some(e => !e.tipo || !e.precio || !e.cantidad)) || (!conEntrada && !descripcion)) {
      alert("Por favor completá todos los campos obligatorios.");
      return;
    }

    const data = {
      nombre,
      lugar,
      fecha,
      urlImg: imagenUrl,
      conEntrada,
      ...(conEntrada ? { entradas } : { descripcion })
    };

    try {
      await axios.post("https://southamerica-east1-snappy-striker-455715-q2.cloudfunctions.net/mains/eventos", data);
      alert("Evento creado correctamente");
      onClose();
    } catch (error) {
      console.error(error);
      alert("Error al crear evento");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 overflow-auto">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg relative">
        <h2 className="text-xl font-bold mb-4 text-center text-[#1D094E]">Crear Evento</h2>

        <InputField label="Nombre del evento" value={nombre} onChange={setNombre} />
        <InputField label="Lugar" value={lugar} onChange={setLugar} />
        <InputField label="Fecha" value={fecha} onChange={setFecha} type="date" />
        <InputField label="Imagen banner (URL)" value={imagenUrl} onChange={setImagenUrl} />

        <div className="flex gap-4 mt-2 mb-4">
          <label className="text-[#1D094E]">
            <input
              type="radio"
              name="entrada"
              checked={conEntrada}
              onChange={() => setConEntrada(true)}
            /> Con entradas
          </label>
          <label className="text-[#1D094E]">
            <input
              type="radio"
              name="entrada"
              checked={!conEntrada}
              onChange={() => setConEntrada(false)}
            /> Sin entradas
          </label>
        </div>

        {conEntrada ? (
          <div className="space-y-2">
            {entradas.map((entrada, i) => (
              <div key={i} className="flex items-center gap-2">
                <InputField label="Tipo" value={entrada.tipo} onChange={(val) => actualizarEntrada(i, "tipo", val)} className="w-1/3" />
                <InputField label="Precio" value={entrada.precio} onChange={(val) => actualizarEntrada(i, "precio", val)} className="w-1/3" />
                <InputField label="Cantidad" value={entrada.cantidad} onChange={(val) => actualizarEntrada(i, "cantidad", val)} className="w-1/3" />
                <button
                  className="text-white bg-[#1D094E] rounded-full w-6 h-6 text-sm"
                  onClick={() => eliminarFila(i)}>
                  -
                </button>
              </div>
            ))}
            <button className="text-white bg-[#1D094E] px-3 py-1 rounded-full mt-2" onClick={agregarFila}>+</button>
          </div>
        ) : (
          <InputField label="Descripción del evento" value={descripcion} onChange={setDescripcion} />
        )}

        <div className="flex justify-end gap-4 mt-6">
          <SimpleButton onClick={onClose} className="bg-black-300 text-gray-700 rounded-full px-4 py-2">
            Cancelar
          </SimpleButton>
          <NeonButton onClick={enviarFormulario}>
            Confirmar
          </NeonButton>
        </div>
      </div>
    </div>
  );
}
