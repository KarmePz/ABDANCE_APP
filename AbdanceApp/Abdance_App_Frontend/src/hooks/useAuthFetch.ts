import {useState, useEffect} from "react";

type UseAuthFetchResult<T> = {
    data: T | null;
    loading: boolean;
    error: string | null;
}



export function useAuthFetch<T = any>(url: string): UseAuthFetchResult<T> {
    const [data, setData] = useState<T | null> (null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect( () =>{
        const fetchData = async() =>{
            setLoading(true);
            setError(null);

            const token = localStorage.getItem("token");//Se pide el token guardado en el local storage

            console.log("Token usado en fetch:", token)
            
            if (!token){
                setError("No se encontro el token.") //si no se encuentra el token se termina la ejecucion
                setLoading(false);
                return
            }

            try{
                const response = await fetch(url, {
                    headers:{
                        Authorization :`Bearer ${token}`,
                        "Content-Type" : "application/json",
                    },
                });

                const rawText = await response.text();
                
                if(!response.ok){
                    if (response.status == 403){
                        throw new Error ("Error al obtener los datos. Permisos insuficientes")
                    }
                    throw new Error("Error al obtener los datos.");
                }

                try {
                    const jsonData: T = JSON.parse(rawText);
                    setData(jsonData);
                } catch {
                    console.error("Respuesta no es JSON:", rawText);
                    setError("Respuesta no válida en formato JSON.");
                }
                
                
                // const jsonData: T = await response.json();
                // setData(jsonData);
            }catch(err : any){
                setError(err.message || "Error desconocido");
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, [url]);

    return { data, loading, error};
}
