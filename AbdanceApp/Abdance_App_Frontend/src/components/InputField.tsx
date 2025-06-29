// InputField.tsx
//import React from 'react';

// Define las props para tu InputField
interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string; // Propiedad opcional para el tipo de input (text, date, etc.)
  // Aquí es donde agregamos la propiedad 'readOnly'
  readOnly?: boolean; // <--- ¡Esta es la línea clave que necesitas añadir!
  placeholder?: string; // Si ya lo tenías, mantenlo.
  className?: string; // Si ya lo tenías, mantenlo.
}

export default function InputField({
  label,
  value,
  onChange,
  type = "text",
  readOnly = false,
  placeholder,
  className
}: InputFieldProps) {
  return (
    <div className="mb-4">
      <label className="block text-[#1D094E] text-base font-semibold mb-2">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        readOnly={readOnly}
        placeholder={placeholder}
        className={`
          w-full 
          p-3 
          bg-[#1D094E] 
          text-white 
          border border-transparent 
          rounded-2xl 
          focus:outline-none 
          focus:ring-2 
          focus:ring-white 
          placeholder-white 
          ${className || ''}
        `}
      />
    </div>
  );
}
