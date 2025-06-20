import { FaCircleCheck, FaCircleExclamation } from "react-icons/fa6";
import NeonButton from "./NeonButton";
import SimpleButton from "./SimpleButton";

interface Entrada {
  id: string;
  nombre: string;
  apellido: string;
  dni: string;
  email: string;
  tipo_entrada: string;
  estado: string;
}

interface Props {
  entrada: Entrada;
  onClose: () => void;
  onValidar: () => void;
}

const ValidarEntradaModal = ({ entrada, onClose, onValidar }: Props) => {
  const yaValidada = entrada.estado === "validada";

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
      <div
        className={`rounded-xl p-6 w-[300px] text-center shadow-xl border-4 ${
          yaValidada ? "border-red-500" : "border-green-500"
        }`}
        style={{
          background: "linear-gradient(180deg, #270359 0%, #5406BF 100%)",
        }}
      >
        <div className="text-5xl mb-3 flex justify-center">
          {yaValidada ? (
            <FaCircleExclamation className="text-red-500" />
          ) : (
            <FaCircleCheck className="text-green-500" />
          )}
        </div>
        <h2 className={`text-white font-semibold mb-2`}>
          {yaValidada ? "La entrada ya fue validada." : "Validar Entrada"}
        </h2>
        <div className="text-white text-sm text-left mb-4">
          <p>
            <strong>ID Ticket:</strong> {entrada.id}
          </p>
          <p>
            <strong>Nombre:</strong> {entrada.nombre} {entrada.apellido}
          </p>
          <p>
            <strong>Email:</strong> {entrada.email}
          </p>
          <p>
            <strong>DNI:</strong> {entrada.dni}
          </p>
          <p>
            <strong>Estado:</strong> {entrada.estado}
          </p>
        </div>

        <div className="flex justify-between">
          <SimpleButton onClick={onClose}>Volver</SimpleButton>
          {!yaValidada && (
            <NeonButton onClick={onValidar}>Validar</NeonButton>
          )}
        </div>
      </div>
    </div>
  );
};

export default ValidarEntradaModal;
