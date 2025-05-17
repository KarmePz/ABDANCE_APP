
import firebase_admin
from firebase_admin import auth
from functools import wraps
from firebase_init import db  # Firebase con base de datos inicializada


# Decorador para autenticar y autorizar con roles
def require_auth(required_roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            id_token = request.headers.get('Authorization')
            if not id_token or not id_token.startswith("Bearer "):
                return {'error': 'Token faltante o formato incorrecto'}, 401

            id_token = id_token.split(" ")[1]  # Obtener token sin 'Bearer'
            try:
                # Verificar el token
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']
                # Obtener el rol del usuario desde Firestore
                user_role = get_user_role_from_firestore(uid)
                
                if required_roles and user_role not in required_roles:
                    return {'error': 'Acceso no autorizado'}, 403
                
                # Añadir uid y rol al contexto de la solicitud
                kwargs['uid'] = uid
                kwargs['role'] = user_role
                
                # Continuar con la función original
                return f(request, *args, **kwargs)

            except auth.InvalidIdTokenError:
                return {'error': 'Token inválido'}, 401
            except Exception as e:
                return {'error': str(e)}, 500  # Maneja otros errores generales

        return wrapper
    return decorator

# Obtener el rol del usuario desde Firestore
def get_user_role_from_firestore(uid):
    user_ref = db.collection("usuarios")
    query = user_ref.where("user_uid", "==", uid).limit(1).stream()
    
    for doc in query:
        user_data = doc.to_dict()
        return user_data.get("rol")  # Asumiendo que el campo es "rol"
    
    return None  # No se encontró el rol del usuario