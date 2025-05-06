from flask import Flask, request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from functools import wraps


#decorador para definir que roles pueden acceder a los metodos
def require_auth(required_roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            id_token = request.headers.get('Authorization')
            if not id_token or not id_token.startswith("Bearer "):
                return jsonify({'error': 'Token faltante o formato incorrecto'}), 401
            id_token = id_token.split(" ")[1]
            try:
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']
                user_role = get_user_role_from_firestore(uid)
                
                if required_roles and user_role not in required_roles:
                    return jsonify({'error': 'Acceso no autorizado'}), 403
                
                # Pasar UID y rol como argumentos
                return f(uid=uid, role=user_role, *args, **kwargs)
            except auth.InvalidIdTokenError:
                return jsonify({'error': 'Token inválido'}), 401
            except Exception as e:
                return jsonify({'error': str(e)}), 500  # Maneja otros errores generales

        return wrapper
    return decorator


#obtener el rol del usuario para autenticarlo
def get_user_role_from_firestore(uid):
    user_ref = db.collection("usuarios")
    query = user_ref.where("user_uid", "==", uid).limit(1).stream()
    
    for doc in query:
        user_data = doc.to_dict()
        return user_data.get("rol")  # Asegurate de que el campo se llame "rol"

    return None  # No se encontró ningún usuario con ese UID