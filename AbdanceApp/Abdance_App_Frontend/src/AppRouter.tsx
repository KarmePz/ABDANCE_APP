import { ReactNode } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import App from "./App";
import { PrivateGuard } from "./guard/PrivateGuard";

interface Props{
    children : ReactNode
}

export const AppRouter = ({children}:Props) =>{
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<App/>} />
                <Route element={<PrivateGuard />} >
                    {/* RUTA PRIVADA */}
                    <Route path="/private" element={<App/>} /> 
                </Route>
            </Routes>
        </BrowserRouter>
    )
}