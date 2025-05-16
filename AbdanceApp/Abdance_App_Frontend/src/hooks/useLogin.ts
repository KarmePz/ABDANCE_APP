import { getIdToken, signInWithEmailAndPassword } from "firebase/auth";
import { useState } from "react";
import { auth } from "../firebase-config";


export const useLogin= () =>{

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const login = async(email:string, password:string) =>{
        //se setea el loading en true y el error en null.
        setLoading(true);
        setError(null);
        
        //se usa un try-catch para intentar iniciar sesion:
        try{
            const credencialUsuario = await signInWithEmailAndPassword(auth,email, password); //se inicia sesion con las credenciales del usuario
            const usuario = credencialUsuario.user;//se obtiene el usuario asociado con el token
            const bearerToken = await getIdToken(usuario);

            //se guarda el token en la localstorage
            localStorage.setItem("token", bearerToken);

            return { usuario, bearerToken }; 

        }catch(error:any){
            setError(error.message);
            if (error.message == "Firebase: Error (auth/invalid-credential)."){
                setError("El email o contraseña son incorrectos")
            }
            return false;
        }finally{
            setLoading(false);
        }
    };
    return {login, loading, error};
}