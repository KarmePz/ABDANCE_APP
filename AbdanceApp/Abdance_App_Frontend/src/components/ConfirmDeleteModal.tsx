// src/components/ConfirmDeleteModal.tsx

import React, { useState } from 'react';
import { FaExclamationTriangle } from 'react-icons/fa'; // Importa un ícono de advertencia de react-icons/fa

interface ConfirmDeleteModalProps {
  onConfirm: () => void; // Función a llamar si el usuario confirma
  onCancel: () => void;   // Función a llamar si el usuario cancela
}

const ConfirmDeleteModal: React.FC<ConfirmDeleteModalProps> = ({ onConfirm, onCancel }) => {
  const [inputValue, setInputValue] = useState('');
  const isConfirmEnabled = inputValue.toLowerCase() === 'confirmar';

  const handleConfirmClick = () => {
    if (isConfirmEnabled) {
      onConfirm();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-xl p-8 w-full max-w-sm shadow-lg relative text-center text-[#1D094E]">
        <div className="mb-6">
          <FaExclamationTriangle className="mx-auto h-20 w-20 text-yellow-500" /> {/* Ícono de advertencia */}
        </div>
        <h2 className="text-xl font-bold mb-4">
          ¿Estás seguro que deseas eliminar el evento?
        </h2>
        <p className="text-sm mb-6">
          Escribe "confirmar" para eliminarlo.
        </p>
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="escribe aquí..."
          className="w-full p-3 mb-6 rounded-full bg-[#1D094E] text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#6b47c0] text-center"
        />
        <div className="flex justify-center gap-4">
          <button
            onClick={onCancel}
            className="rounded-full px-6 py-3 font-semibold bg-transparent text-[#1D094E] border border-[#1D094E] hover:bg-[#efefef] transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirmClick}
            disabled={!isConfirmEnabled} // Deshabilitado hasta que se escriba "confirmar"
            className={`rounded-full px-6 py-3 font-semibold transition-colors
              ${isConfirmEnabled
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDeleteModal;