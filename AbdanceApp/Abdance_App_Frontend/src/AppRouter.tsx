import { ReactNode } from "react";
import {  Navigate, Route, Routes } from "react-router-dom";
import App from "./App";
import { PrivateGuard } from "./guard/PrivateGuard";
import Dashboard from "./pages/Dashboard";

interface Props{
    children : ReactNode
}

export const AppRouter = ({children}:Props) =>{
    return (
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<App/>} />

                <Route element={<PrivateGuard />} >
                    {/* RUTA PRIVADA */}
                    <Route path="/private" element={<Dashboard/>} /> 
                </Route>
            </Routes>
        
    )
}