/* TODO: ESTO ES SOLO UN COMPONENTE PARA TESTING 
SE DEBE INTEGRAR EL COMPONENTE NECESARIO AL CHECKOUT PRO*/
import reactImg from "./../../assets/react.svg"
import "./Pagos.css"
import { initMercadoPago, Wallet } from '@mercadopago/sdk-react';

initMercadoPago('YOUR_PUBLIC_KEY');

export default function PagosTest() {
    return (
        <div className="card-product-container">
            <div className="card-product">
                <div className="card">
                    <img src={reactImg} alt="Checkout Pro representation"></img>
                    <h3>Checkout Pro Testing Integration</h3>
                    <p className="price">100$</p>
                    <button>Pagar</button>
                </div>
            </div>
        </div>
    )
}