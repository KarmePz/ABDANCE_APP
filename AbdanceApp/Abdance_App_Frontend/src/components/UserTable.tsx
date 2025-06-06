import { useState } from "react";
import { useAuthFetch } from "../hooks/useAuthFetch";
import { UserFormDialog } from "./UserFormDialog";

type User = {
    id:string;
    dni: string;
    nombre: string;
    apellido: string
    email: string;
    rol: string;
};

export function UserTable() {
    const endpointUrl =  import.meta.env.VITE_API_URL
    const [reloadFlag, setReloadFlag] = useState(0); //controla los cambios de la tabla

    const { data: users, loading, error } = useAuthFetch<User[]>(`${endpointUrl}/usuarios?reload=${reloadFlag}`);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [open, setOpen] = useState(false);

    const handleEdit = (user: User) => {
        setSelectedUser(user);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setSelectedUser(null);
    };
    
  // Esta función se pasa para forzar recarga
    const handleUserUpdated = () => {
        setReloadFlag((prev) => prev + 1);
    };

    if (loading) return <p>Cargando...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <>
        <table className="min-w-full border">
            <thead>
            <tr className="bg-gray-200">
                <th>DNI</th>
                <th>Nombre</th>
                <th>Apellido</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Acciones</th>
            </tr>
            </thead>
            <tbody>
            {users?.map((user) => (
                <tr key={user.dni}>
                <td>{user.dni}</td>
                <td>{user.nombre}</td>
                <td>{user.apellido}</td>
                <td>{user.email}</td>
                <td>{user.rol}</td>
                <td>
                    <button
                    className="bg-blue-500 text-white px-2 py-1 rounded mr-2"
                    onClick={() => handleEdit(user)}
                    >
                    Editar
                    </button>
                </td>
                </tr>
            ))}
            </tbody>
        </table>

        {selectedUser && (
            <UserFormDialog open={open} user={selectedUser} onClose={handleClose} onUserUpdated={handleUserUpdated} />
        )}
        </>
    );
}
