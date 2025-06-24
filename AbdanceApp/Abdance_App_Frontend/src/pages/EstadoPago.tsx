import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SimpleButton from "../components/SimpleButton"; // Asumiendo que tienes este componente

export default function EstadoPago() {
  const location = useLocation();
  const navigate = useNavigate();
  //const [status, setStatus] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const collectionStatus = params.get("collection_status");
    //const externalReference = params.get("external_reference"); // Usado para referencia si se necesita

    //setStatus(collectionStatus);

    switch (collectionStatus) {
      case "approved":
        setMessage(
          "¡Tu pago ha sido **aprobado**! ✅ Recibirás tu/s entrada/s en tu correo electrónico en los próximos minutos. Por favor, revisa tu bandeja de entrada y la carpeta de spam."
        );
        break;
      case "pending":
        setMessage(
          "Tu pago está **pendiente** de confirmación ⏳. Recibirás una notificación por correo electrónico una vez que se procese. Esto puede demorar unos minutos u horas, dependiendo del medio de pago."
        );
        break;
      case "rejected": // Mercado Pago también puede usar "rejected" para fallos
      case "failure": // Puedes tener un 'failure' específico en tu `back_urls`
      default:
        setMessage(
          "Hubo un problema al procesar tu pago. ❌ Por favor, inténtalo de nuevo o contacta con soporte si el problema persiste."
        );
        break;
    }
    setLoading(false);

    // Opcional: Limpiar el localStorage de formularios temporales si existe
    localStorage.removeItem("datosFormEntradas");

  }, [location.search]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#1D094E] text-white p-6 text-center">
        <p>Procesando el estado de tu pago...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#1D094E] text-white p-6 text-center">
      <div className="bg-white bg-opacity-90 p-8 rounded-xl shadow-2xl text-[#1D094E] max-w-xl w-full">
        <h1 className="text-3xl font-bold mb-6">Estado de tu Transacción</h1>
        <p className="text-xl leading-relaxed mb-8" dangerouslySetInnerHTML={{ __html: message }}></p>
        
        <SimpleButton onClick={() => navigate("/")}>Volver al Inicio</SimpleButton>
      </div>
    </div>
  );
}