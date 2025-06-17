import axios from "axios";
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';
import { useState } from "react";

export default function PagosTest() {
    const publicKey = import.meta.env.MERCADO_PAGO_KEY
    initMercadoPago(publicKey, {
        locale: "es-AR"
    });

    /* Esto se obtendrá de la cuota seleccionada */
    const id_cuota_localStorage = ""

    const [idPreferencia, setIdPreferencia] = useState(null)
    const token = localStorage.getItem("token");

    const crear_preferencia = async () => {
        try {
            const respuesta = await axios.post(
                "http://127.0.0.1:8080/crear_preferencia_cuota",
                {
                    cuota_id: id_cuota_localStorage,
                    dia_recargo: 11
                },
                {
                    headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                    }
                }
                );

            const id = respuesta.data.id
            return id;
            
        } catch (error) {
            console.log(error)
        }
    }

    const return_id_pago = async () => {
        const id = await crear_preferencia()
        if (id) {
            setIdPreferencia(id)
        }
        else {
            console.log("Error al obtener el id de la preferencia.")
        }
    }

    return (
        <div>
            <button onClick={return_id_pago}>Pagar</button>
            <div>
                {idPreferencia && <Wallet initialization={{ preferenceId: idPreferencia }} />}
            </div>
        </div>
    )
}