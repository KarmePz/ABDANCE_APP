import { ReactNode } from "react";
import {  Navigate, Route, Routes } from "react-router-dom";
import App from "./App";
import { PrivateGuard } from "./guard/PrivateGuard";
import Dashboard from "./pages/Dashboard";
import Eventos from "./pages/Eventos";
import EventoDetalle from "./pages/EventoDetalle"; 
import FormularioEntradasPage from './pages/FormularioEntradasPage';
import PagoExitoso from "./pages/PagoExitosoPage";

interface Props{
    children : ReactNode
}

export const AppRouter = ({children}:Props) =>{
    return (
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<App/>} />
                <Route path="/eventos" element={<Eventos />} />
                <Route path="/" element={<Eventos />} />
                <Route path="/evento/:id" element={<EventoDetalle />} />
                <Route path="/formulario-entradas" element={<FormularioEntradasPage />} />
                <Route path="/pago-exitoso" element={<PagoExitoso />} />

                <Route element={<PrivateGuard />} >
                    {/* RUTA PRIVADA */}
                    <Route path="/private" element={<Dashboard/>} /> 
                </Route>
            </Routes>
        
    )
}