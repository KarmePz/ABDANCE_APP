import { ReactNode, useState } from 'react';
import {UserTable} from '../components'
import { CreateUserForm } from '../components/UserComponents/CreateUserForm';
import { DisciplineStudentsTable } from '../components/InasistenciaComponents/DisciplineStudentsTable';



interface Props{
    children?: ReactNode;
}

export const InasistenciaContentDashboard = ({children}: Props) =>{
    const [reloadFlag, setReloadFlag] = useState(0); // Para actualizar studentTable
    // const [openCreate] = useState(false); // Controla modal creación

    // const handleUserCreated = () => {
    //     // Fuerza reload en UserTable
    //     handleUserUpdated();
    //     setOpenCreate(false); // Cierra modal
    // };

    const handleUserUpdated = () => {
        setReloadFlag((prev) => prev + 1); // Fuerza recarga
    };

    return (
        <>
        <h1 className="text-2xl font-bold mb-4">USUARIOS</h1>

        {/* Pasamos reloadFlag a UserTable como prop */}
        <DisciplineStudentsTable reloadFlag={reloadFlag} onUserUpdated={handleUserUpdated} disciplinaId='AXNhrGdDDZ7vFbDaSKiT' />

        {/* Modal para crear usuario */}
        {/* <button
        onClick={() => setOpenCreate(true)}
        className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
            Crear Usuario
        </button>

        {openCreate && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full relative">
                <button
                onClick={() => setOpenCreate(false)}
                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
                >
                ✕
                </button>
                <h2 className="text-xl font-bold mb-4">Crear nuevo usuario</h2>
                <CreateUserForm onUserCreated={handleUserCreated} /> */}
            {/* </div>
            </div>
        )} */}
        </>
    );
}
export default InasistenciaContentDashboard;

