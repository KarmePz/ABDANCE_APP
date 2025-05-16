import { Control, Controller, FieldError } from "react-hook-form";

interface Props {
    name: string;
    control: Control<any>;
    label : string;
    type?: string;
    error?: FieldError
}

const InputForm = ({name, control, label, type, error}: Props) =>{
    
    return (
            <div className="form-group ">
                <label htmlFor={name} >{label}</label>
                <Controller 
                name={name} 
                control={control} 
                render={({field}) => 
                <input id={name} type={type} {...field} className={`
                    p-2 border border-gray-300 rounded w-full bg-gray-800 text-gray-200 
                    form-control ${error ? "is-invalid": ''}
                    `} placeholder={label}/> } 
                />
                {error && <p className="error text-red-600">{error.message}</p>}
            </div>
    )
} 

export default InputForm;