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
                <label htmlFor={name}>{label}</label>
                <Controller 
                name={name} 
                control={control} 
                render={({field}) => <input id={name} type={type} {...field} className={`form-control ${error ? "is-invalid": ''} `}  /> } 
                />
                {error && <p className="error text-red-600">{error.message}</p>}
            </div>
    )
} 

export default InputForm;