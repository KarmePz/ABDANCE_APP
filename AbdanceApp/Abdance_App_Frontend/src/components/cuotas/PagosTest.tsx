/* TODO: ESTO ES SOLO UN COMPONENTE PARA TESTING 
SE DEBE INTEGRAR EL COMPONENTE NECESARIO AL CHECKOUT PRO*/
import axios from "axios";
import danceImg from "./../../../public/dance.ico"
import "./Pagos.css"
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';
import { useState } from "react";

export default function PagosTest() {
    /* TODO: GET THIS THING OUT OF HERE */
    const publicKey = "APP_USR-5f823e37-e3e9-4c4c-9d9d-ff696f47ba7d" 
    initMercadoPago(publicKey, {
        locale: "es-AR"
    });

    /* TODO: PONER ESTO EN EL LOCAL STORAGE, O EN OTRO LUGAR */
    const id_pago_localStorage = "1CcsWhRmtA8tDckwFtn5"

    const [idPreferencia, setIdPreferencia] = useState(null)

    const crear_preferencia = async () => {
        try {
            const respuesta = await axios.post("http://127.0.0.1:8080/efectuar_pago", {
                cuota_id: id_pago_localStorage,
                dia_recargo: 11
            })
            
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
        <div className="card-product-container">
            <div className="card-product">
                <div className="card">
                    <img src={danceImg} alt="Checkout Pro representation"></img>
                    <h3>Checkout Pro Testing Integration</h3>
                    <p className="price">100$</p>
                    <button onClick={return_id_pago}>Pagar</button>
                    <div>
                        {idPreferencia && <Wallet initialization={{ preferenceId: idPreferencia }} />}
                    </div>
                </div>
            </div>
        </div>
    )

    /*
    */ 
}