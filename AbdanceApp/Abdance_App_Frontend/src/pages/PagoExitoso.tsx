import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function PagoExitosoPage() {
  const [mensaje, setMensaje] = useState("Procesando tu compra...");
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const endpointUrl =  import.meta.env.VITE_API_URL_DEV;//modo dev
  //const endpointUrl= "https://def456.ngrok-free.app"//para preubas en ngrok

  useEffect(() => {
    const eventoId = searchParams.get("eventoId");
    const formId = searchParams.get("formId");

    if (!eventoId || !formId) {
      setMensaje("Faltan datos para procesar las entradas.");
      return;
    }

    console.log("📤 Enviando confirmación:", { eventoId, formId });
    //https://959f-190-183-84-54.ngrok-free.app
    //http://localhost:5000
    fetch(`${endpointUrl}/api/registrar_entradas`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        evento_id: eventoId,
        form_id: formId
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.ok || data.mensaje) {
          setMensaje("¡Entradas registradas correctamente! Revisa tu correo con el QR.");
        } else {
          setMensaje("Ocurrió un error: " + (data.error || "desconocido."));
        }
      })
      .catch((err) => {
        console.error("❌ Error en el fetch:", err);
        setMensaje("Error en la comunicación con el servidor.");
      });
  }, []);

  return (
    <div className="text-white text-center mt-20 font-sans">
      <h1 className="text-2xl font-bold">{mensaje}</h1>
      <button
        onClick={() => navigate("/")}
        className="mt-8 px-4 py-2 bg-purple-600 rounded hover:bg-purple-700 transition"
      >
        Volver al inicio
      </button>
    </div>
  );
}
