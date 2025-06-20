import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import FormularioEntrada, { DatosFormulario } from "../components/FormularioEntrada";
import NeonButton from "../components/NeonButton";
import SimpleButton from "../components/SimpleButton";
import MensajeAlerta from "../components/MensajeAlerta";

const STORAGE_KEY = "datosFormEntradas";

export default function FormularioEntradasPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { entradasSeleccionadas, eventoId, evento } = location.state || {};

  const entradas: { tipo: string; cantidad: number }[] = entradasSeleccionadas || [];

  const formularios: { tipo: string }[] = entradas.flatMap((entrada) =>
    Array(entrada.cantidad).fill({ tipo: entrada.tipo })
  );

  const [formIndex, setFormIndex] = useState(0);
  const [mostrarAdvertencia, setMostrarAdvertencia] = useState(false);
  const [errores, setErrores] = useState<{ [campo: string]: boolean }>({});

  const [datos, setDatos] = useState<DatosFormulario[]>(() => {
    const guardado = localStorage.getItem(STORAGE_KEY);
    if (guardado) return JSON.parse(guardado);

    return formularios.map(() => ({
      nombre: "",
      apellido: "",
      dni: "",
      email: "",
      telefono: "",
    }));
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(datos));
  }, [datos]);

  const actualizarDato = (index: number, campo: keyof DatosFormulario, valor: string) => {
    const nuevosDatos = [...datos];
    nuevosDatos[index][campo] = valor;
    setDatos(nuevosDatos);
  };

  const validarFormulario = (): boolean => {
    const datosActuales = datos[formIndex];
    const nuevosErrores: { [campo: string]: boolean } = {};

    nuevosErrores.nombre = !datosActuales.nombre.trim();
    nuevosErrores.apellido = !datosActuales.apellido.trim();
    nuevosErrores.dni = !/^\d{8}$/.test(datosActuales.dni);
    nuevosErrores.email = !/^[\w.-]+@[\w.-]+\.\w{2,}$/.test(datosActuales.email);
    nuevosErrores.telefono = !/^\d{10,15}$/.test(datosActuales.telefono);

    setErrores(nuevosErrores);
    return !Object.values(nuevosErrores).some(Boolean);
  };

  const avanzar = async () => {
    if (!validarFormulario()) return;

    if (formIndex < formularios.length - 1) {
      setFormIndex(formIndex + 1);
    } else {
      if (!mostrarAdvertencia) {
        setMostrarAdvertencia(true);
      } else {
        await crearPreferenciaPago();
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  };

  const retroceder = () => {
    if (formIndex > 0) {
      setFormIndex(formIndex - 1);
    } else {
      localStorage.removeItem(STORAGE_KEY);
      navigate(`/evento/${eventoId}`);
    }
  };

  const crearPreferenciaPago = async () => {
    try {
      if (!evento || !evento.entradas) {
        throw new Error("No se encontraron precios para este evento.");
      }

      const precios = evento.entradas.reduce((acc: any, entrada: any) => {
        acc[entrada.tipo] = entrada.precio;
        return acc;
      }, {});

      const entradasConPrecio = entradas.map((entrada) => ({
        tipo: entrada.tipo,
        cantidad: entrada.cantidad,
        precio: precios[entrada.tipo] || 0,
      }));

      // 💾 1. Guardar formularios temporales en backend
      const guardarRes = await fetch("http://localhost:5000/formularios-temporales", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evento_id: eventoId,
          formularios: datos,
          entradas: entradasConPrecio,
        }),
      });

      const guardarData = await guardarRes.json();
      if (!guardarRes.ok || !guardarData.formId) {
        throw new Error("No se pudo guardar los formularios.");
      }

      const formId = guardarData.formId;
      console.log("📦 Enviando a backend:", {
        evento_id: eventoId,
        datos,
      });

      // 📤 2. Crear preferencia de pago
      const response = await fetch("http://localhost:5000/crear_preferencia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evento_id: eventoId,
          nombreEvento: evento?.nombre || "",
          lugar: evento?.lugar || "",
          fecha: evento?.fecha || "",
          imagen: evento?.imagen || "",
          entradas: entradasConPrecio,
          form_id: formId, // 🔁 ¡importante! se usa en el retorno
        }),
      });

      const data = await response.json();
      if (data.init_point) {
        window.location.href = data.init_point;
      } else {
        alert("Error al generar preferencia de pago.");
      }
    } catch (error) {
      console.error("Error creando preferencia:", error);
      alert("Ocurrió un error al procesar el pago.");
    }
  };

  if (!datos[formIndex]) {
    return <div className="text-white text-center mt-20">Cargando formulario...</div>;
  }

  return (
    <div className="min-h-screen text-white p-6 flex flex-col items-center justify-center">
      <h1 className="text-2xl text-center font-bold mb-4">Detalles Comprador</h1>

      <FormularioEntrada
        index={formIndex}
        tipoEntrada={formularios[formIndex]?.tipo}
        datos={datos[formIndex]}
        onChange={actualizarDato}
        errores={errores}
      />

      {mostrarAdvertencia && (
        <MensajeAlerta
          tipo="advertencia"
          mensaje="Una vez que hagas clic para Confirmar, se te redireccionará a MercadoPago. Asegurate que los datos estén bien."
        />
      )}

      <div className="flex justify-between w-full max-w-sm mt-8">
        <SimpleButton onClick={retroceder}>Volver</SimpleButton>
        <NeonButton onClick={avanzar}>
          {formIndex < formularios.length - 1
            ? "Siguiente"
            : mostrarAdvertencia
            ? "Confirmar"
            : "Siguiente"}
        </NeonButton>
      </div>
    </div>
  );
}
