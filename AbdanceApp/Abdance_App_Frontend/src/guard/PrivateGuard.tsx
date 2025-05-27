import { Navigate, Outlet } from "react-router-dom";

export const PrivateGuard = ({ RolesPermitidos }: { RolesPermitidos?: string[] }) => {
    const token = localStorage.getItem("token");
    const usuarioString = localStorage.getItem("usuario");
    const usuario = usuarioString ? JSON.parse(usuarioString) : null;
    const rol = usuario?.rol;

    if (!token || !usuario) {
        return <Navigate to="/login" replace />;
    }
     // Si allowedRoles viene y el rol no está permitido, redirige (por ej a un "403" o login)
    if (RolesPermitidos && !RolesPermitidos.includes(rol)) {
        return <Navigate to="/login" replace />;
    }

    // Si todo ok, muestra la ruta protegida
    return <Outlet />;

    
}