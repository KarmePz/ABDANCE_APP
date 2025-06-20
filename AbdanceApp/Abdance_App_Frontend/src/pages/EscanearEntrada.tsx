import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from "react-router-dom";
import ValidarEntradaModal from "../components/ValidarEntradaModal";
import { FaSearch, FaExpand } from "react-icons/fa";

const EscanearEntrada = () => {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [entrada, setEntrada] = useState<any>(null);
  const [mostrarModal, setMostrarModal] = useState(false);
  const navigate = useNavigate();
  const endpointUrl =  import.meta.env.VITE_API_URL_DEV;//modo dev

  const obtenerEntrada = async (codigo: string, eventoId: string) => {
    try {
      const respuesta = await fetch(`${endpointUrl}/entradas?evento_id=${eventoId}`);
      const data = await respuesta.json();
      const entradaEncontrada = data.find((entrada: any) => entrada.id === codigo);

      if (!entradaEncontrada) {
        alert("Entrada no encontrada.");
        return;
      }

      setEntrada({ ...entradaEncontrada, evento_id: eventoId });
      setMostrarModal(true);
    } catch (error) {
      alert("No se pudo obtener la entrada.");
    }
  };

  const handleValidar = async () => {
    if (!entrada) return;
    try {
      const respuesta = await fetch(`${endpointUrl}/entradas`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entrada_id: entrada.id,
          evento_id: entrada.evento_id,
          estado: "validada",
        }),
      });
      const data = await respuesta.json();
      alert(data.mensaje);
      setMostrarModal(false);
      iniciarScanner();
    } catch (error) {
      alert("Error al validar entrada.");
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const qrCodeScanner = new Html5Qrcode("qr-reader");
    const eventoId = localStorage.getItem("evento_seleccionado");

    try {
      const result = await qrCodeScanner.scanFile(file, true);
      if (result && eventoId) {
        await obtenerEntrada(result, eventoId);
      }
    } catch (error) {
      alert("No se pudo escanear la imagen.");
    }
  };

  const iniciarScanner = async () => {
    const eventoId = localStorage.getItem("evento_seleccionado");
    const qrReaderElement = document.getElementById("qr-reader");
    if (!eventoId || !qrReaderElement) return;

    if (scannerRef.current && scannerRef.current.isScanning) return; // evitar duplicados

    if (!scannerRef.current) {
      scannerRef.current = new Html5Qrcode("qr-reader");
    }

    try {
      await scannerRef.current.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: 250 },
        async (decodedText) => {
          if (scannerRef.current?.isScanning) {
            await scannerRef.current.stop();
          }
          await obtenerEntrada(decodedText, eventoId);
        },
        (error) => console.warn("Error escaneando:", error)
      );
    } catch (err) {
      console.error("Error iniciando la cámara:", err);
    }
  };

  const detenerScanner = async () => {
    if (scannerRef.current?.isScanning) {
      await scannerRef.current.stop();
    }
    await scannerRef.current?.clear();
  };

  useEffect(() => {
    const eventoId = localStorage.getItem("evento_seleccionado");
    if (!eventoId) {
      alert("No hay evento seleccionado. Volvé al dashboard.");
      navigate("/dashboard");
      return;
    }

    iniciarScanner();

    return () => {
      detenerScanner();
    };
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4 text-center">Escanear entrada</h1>

      <div id="qr-reader" className="w-full max-w-md mx-auto" />

      <div className="mt-6 text-center">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          O subí una imagen con un código QR:
        </label>
        <input type="file" accept="image/*" onChange={handleImageUpload} className="mx-auto" />
      </div>

      {mostrarModal && entrada && (
        <ValidarEntradaModal
          entrada={entrada}
          onClose={() => {
            setMostrarModal(false);
            iniciarScanner();
          }}
          onValidar={handleValidar}
        />
      )}

      <div className="flex justify-center gap-6 mt-6">
        {/* Botón que redirige a /dashboard/entradas */}
        <button
          className="text-white text-3xl"
          onClick={() => {
            detenerScanner();
            navigate("/dashboard/entradas");
          }}
        >
          <FaSearch />
        </button>

        {/* Botón decorativo */}
        <button className="text-cyan-400 text-3xl">
          <FaExpand />
        </button>
      </div>
    </div>
  );
};

export default EscanearEntrada;
