import { zodResolver } from "@hookform/resolvers/zod";
import {z} from "zod";
import InputForm from "./CustomInput";
import { SubmitHandler, useForm } from "react-hook-form";
import { useLogin } from "../hooks/useLogin";


const schema = z.object({
    email: z.string().email("Correo invalido").min(1, "El correo es obligatorio"),
    password: z.string().min(6, "La contraseña debe de tener al menos 6 caracteres"),
})


type FormValues = z.infer<typeof schema>;

const LoginForm = () => {

    const { login, loading, error } = useLogin();

    const {control, handleSubmit, formState: {errors}} = useForm<FormValues>({
        resolver: zodResolver(schema)
    });
const onSubmit: SubmitHandler<FormValues> = async (data) =>{
    console.log(data);
    const resultado = await login(data.email, data.password);
    if (resultado) {
        window.location.href = "https://www.youtube.com";
    }
}

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="z-30">
            <InputForm name='email'control={control} label="Email" type="email" error={errors.email}  />
            <InputForm name='password'control={control} label="Password" type="password" error={errors.password} />

            <button type="submit" className="m-2" disabled={loading}>{loading ? "Cargando": "Iniciar Sesión"}</button>
            {error && <p className="text-red-500 bg-amber-100">{error}</p>}
        </form>
    )
}

export default LoginForm