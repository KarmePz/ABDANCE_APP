import { ReactNode } from "react";
import {  Navigate, Route, Routes } from "react-router-dom"; 
import App from "./App";
import { PrivateGuard } from "./guard/PrivateGuard";
import { Loader} from './components'
import Dashboard from "./pages/Dashboard";


interface Props{
    children : ReactNode
}

export const AppRouter = ({children}:Props) =>{
    return (
                <RoutesWithNoFound>
                    <Route path="/" element={<Navigate to="/login" replace/>} />
                    <Route path="/login" element={<App/>} />
                    <Route path="/eventos" element={<h1>Esta es la pestaña de eventos</h1>} />
                    <Route path="/eventos/evento_id" element={<h1>Esta es la pestaña de un evento Id particular</h1>} />
                    <Route path="/eventos/evento_id/compra" element={<h1>Esta es la pestaña de compra de un evento particular</h1>} />
                

                <Route element={<PrivateGuard   />} >

                    {/* RUTA PRIVADA */}
                        <Route path="/dashboard" element={<Dashboard/>} > 
                            <Route path="" element={<h1>Inicio</h1>}/>
                            <Route path="eventos" element={<h1>Eventos</h1>} />
                            <Route path="eventos/agregar" element={<Dashboard/>} />
                            <Route path="/dashboard/eventos/id_evento" element={<Dashboard/>} />
                            <Route path="/dashboard/eventos/id_evento/comprar" element={<Dashboard/>} />

                            <Route path="usuarios" element={<UserContentDashboard />} />
                            <Route path="/dashboard/usuarios/agregar" element={<Dashboard/>} />
                            <Route path="/dashboard/usuarios/id_usuario" element={<Dashboard/>} />

                            <Route path="/dashboard/disciplinas" element={<DisciplinaContentDashboard/>} />
                            <Route path="/dashboard/disciplinas/agregar" element={<Dashboard/>} />
                            <Route path="/dashboard/disciplinas/id_disciplina" element={<Dashboard/>} />

                            <Route path="/dashboard/asistencias" element={<InasistenciaContentDashboard />} />
                            <Route path="/dashboard/asistencias/alumno_dni" element={<Dashboard/>} />
                            

                            <Route path="/dashboard/cuotas" element={<div className="flex justify-center align-middle items-center w-full h-full"><Loader /></div>} />
                            <Route path="/dashboard/cuotas/alumno_dni" element={<Dashboard/>} />
                            <Route path="/dashboard/cuotas/alumno_dni/id_cuota" element={<Dashboard/>} />

                            <Route path="/dashboard/entradas" element={<h1>ENTRADAS</h1>} />
                            <Route path="/dashboard/estadisticas" element={<h1>ESTADISTICAS</h1>} />
                        </Route>
                </Route>
                

                <Route element={<PrivateGuard RolesPermitidos={["profesor"]} />}>
                    <Route path="/dashboard/asistencias/tomar_asistencia" element={<h1>ACA SE TOMA ASISTENCIA </h1>} />
                
                
                
                </Route>
                <Route path="/403" element={<Page_403 />} />
                </RoutesWithNoFound>
                /* Rutas no existentes/encontradas */
            
        
    )
}


import { Page_404 } from "./pages/Page_404";
import { Page_403 } from "./pages/Page_403";
import UserContentDashboard from "./pages/UserContentDashboard";
import InasistenciaContentDashboard from "./pages/InasistenciaContentDashboard";
import DisciplinaContentDashboard from "./pages/DisciplinaContentDashboard";
interface Props{
    children: ReactNode
}
export const RoutesWithNoFound = ({children}: Props) => {
    return (
    <Routes>
        {children}
        <Route path="*" element={<Navigate to="/404" />}/>
        <Route path="/404" element={<Page_404 /> } />
    </Routes>
    )
}