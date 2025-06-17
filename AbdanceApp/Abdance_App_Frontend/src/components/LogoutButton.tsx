import React from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../firebase-config';
import { signOut } from 'firebase/auth';

    const LogoutButton = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
        await signOut(auth);
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
        navigate('/login');
        } catch (error) {
        console.error('Error al cerrar sesión:', error);
        }
    };

    return (
        <button
        onClick={handleLogout}
        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 transition-colors duration-200"
        >
        Cerrar Sesión
        </button>
    );
};

export default LogoutButton;