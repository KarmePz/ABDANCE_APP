/* TODO: ESTO ES SOLO UN COMPONENTE PARA TESTING 
SE DEBE INTEGRAR EL COMPONENTE NECESARIO AL CHECKOUT PRO*/
import danceImg from "./../../../public/dance.ico"
import "./Pagos.css"
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';

export default function PagosTest() {
    /* TODO: GET THIS THING OUT OF HERE */
    const publicKey = "APP_USR-5f823e37-e3e9-4c4c-9d9d-ff696f47ba7d" 
    initMercadoPago(publicKey, {
        locale: "es-AR"
    });

    return (
        <div className="card-product-container">
            <div className="card-product">
                <div className="card">
                    <img src={danceImg} alt="Checkout Pro representation"></img>
                    <h3>Checkout Pro Testing Integration</h3>
                    <p className="price">100$</p>
                    <button>Pagar</button>
                    <div>
                        <Wallet initialization={{ preferenceId: 'YOUR_PREFERENCE_ID' }} />
                    </div>
                </div>
            </div>
        </div>
    )
}