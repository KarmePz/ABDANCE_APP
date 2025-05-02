from flask import Flask, request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from .auth_decorator import require_auth
from functools import wraps




@require_auth(required_roles=['admin', 'profesor'])
def register_student(request):
    #Se piden los datos del usuario, para poder registrarlo
    data = request.json 
    
    #datos relevantes
    student_dni = data.get("dni")
    student_apellido = data.get("apellido")
    student_name = data.get("nombre")
    student_email = data.get("email")
    student_birthdate = data.get("fechaNacimiento") #firestore timeStamp
    student_registrationDate = data.get("fechaInscripcion")#firestore timeStamp
    student_username = data.get("nombreAcceso")
    rol = "alumno"
    
    #se verifica que no falte nada
    if not student_dni or not student_apellido or not student_name or not student_email:
        return {'Error':'Faltan datos, revise dni, nombre, apellido, correo electronico'}, 400
    
    # Intenta parsear las fechas si vienen como string
    try:
        birthdate = datetime.fromisoformat(student_birthdate) if student_birthdate else None
        registration_date = datetime.fromisoformat(student_registrationDate) if student_registrationDate else None
    except ValueError:
        return {'error': 'Formato de fecha inválido'}, 400
    
    try:
        #se crea el usuario usando su email como email de ingreso y su dni como su contraseña
        usuario = auth.create_user(email=student_email, password=str(student_dni))
        
        db.collection("usuarios").document(str(student_dni)).set(
            {
                'dni':student_dni,
                'apellido':student_apellido,
                'nombre': student_name,
                'email':student_email,
                'fechaNacimiento':birthdate,
                'fechaInscripcion':registration_date,
                'nombreAcceso':student_username,
                'rol':'alumno',
                'user_uid': usuario.uid 
            }
        )
        
        
        
        return {'message': 'Alumno registrado exitosamente', 'user_id': usuario.uid}, 201
    except Exception as e:
        return {'error': str(e)}, 400

def login_user(request):
    #se quiere devolver el mail del usuario y su contraseña
    #se puede ingresar un username o el mail directo
    #si se ingresa un username este mismo sera el nombre.acceso del firebase 
    return


"""

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

    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get("rol")  # Asegurate de que el campo se llame exactamente "rol"
    else:
        return None
        """