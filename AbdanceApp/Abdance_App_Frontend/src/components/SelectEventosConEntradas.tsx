import { useEffect, useState } from "react";

interface Evento {
  id: string;
  nombre: string;
  codigo: string;
  conEntrada: boolean;
}

interface Props {
  onSelect: (eventoCodigo: string) => void;
}

export const SelectEventosConEntradas = ({ onSelect }: Props) => {
  const [eventos, setEventos] = useState<Evento[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/eventos")
      .then((res) => res.json())
      .then((data) => {
        const eventosConEntrada = data.filter((e: Evento) => e.conEntrada);
        setEventos(eventosConEntrada);
      })
      .catch((err) => console.error("Error cargando eventos:", err));
  }, []);

  return (
    <select
        className="bg-[#1D094E] text-white rounded-xl px-4 py-2 focus:outline-none font-bold"
        onChange={(e) => onSelect(e.target.value)} defaultValue=""
    >
      <option value="" disabled>
        Seleccioná un evento
      </option>
      {eventos.map((evento) => (
        <option key={evento.codigo} value={evento.codigo}>
          {evento.nombre}
        </option>
      ))}
    </select>
  );
};
