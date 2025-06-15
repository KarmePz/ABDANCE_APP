import { useAuthFetch } from "../../hooks/useAuthFetch";

type User = {
    id: string;
    nombre: string;
    email: string;
    rol: string;
};

export function UserTable() {
    const endpointUrl =  import.meta.env.VITE_API_URL

    const { data: users, loading, error } = useAuthFetch<User[]>(`${endpointUrl}/usuarios`);

    if (loading) return <p className="text-gray-500">Cargando usuarios...</p>;
    if (error) return <p className="text-red-500">Error: {error}</p>;
    if (!users || users.length === 0) return <p>No hay usuarios.</p>;

    // const handleEdit = (id: string) => {
    //     console.log(`Editar usuario ${id}`);
    //     // Aquí podrías abrir un modal o redirigir
    // };

     // //metodo eliminar
    // const handleDelete = async (id: string) => {
    //     const token = localStorage.getItem("authToken");
    //     if (!token) {
    //     alert("Token no disponible");
    //     return;
    //     }       
        // try {
        // const res = await fetch(`${endpointUrl}/usuarios`, {
        //     method: "DELETE",
        //     headers: {
        //     Authorization: `Bearer ${token}`,
        //     },
        // });

        // if (!res.ok) throw new Error("Error al eliminar");

        // alert("Usuario eliminado");
        // // podrías hacer un refetch o usar estado para eliminarlo localmente
        // } catch (err) {
        // alert("No se pudo eliminar el usuario");
        // }
    // };

    return (
        <table className="min-w-full table-auto border border-gray-200 shadow-sm rounded-md">
        <thead className="bg-gray-100">
            <tr>
            <th className="px-4 py-2 text-left">Nombre</th>
            <th className="px-4 py-2 text-left">Email</th>
            <th className="px-4 py-2 text-left">Rol</th>
            <th className="px-4 py-2 text-left">Acciones</th>
            </tr>
        </thead>
        <tbody>
            {users.map((user) => (
            <tr key={user.id} className="border-t">
                <td className="px-4 py-2">{user.nombre}</td>
                <td className="px-4 py-2">{user.email}</td>
                <td className="px-4 py-2">{user.rol}</td>
                <td className="px-4 py-2 space-x-2">
                <button
                    // onClick={() => handleEdit(user.id)}
                    className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                >
                    Editar
                </button>
                <button
                    // onClick={() => handleDelete(user.id)}
                    className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                >
                    Eliminar
                </button>
                </td>
            </tr>
            ))}
        </tbody>
        </table>
    );
}