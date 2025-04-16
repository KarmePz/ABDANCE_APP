from flask import Flask, request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime


#TODOS ESTOS METODOS DEBEN SER PROTEGIDOS MEDIANTE EL USO DE VERIFICACION DE TOKENS QUE SE ASIGNEN DESDE EL FRONTEND
#
#De otra manera cualquiera puede acceder a estos datos
#
#Verificar que se cumpla la autenticacion del token y el rol determinado
#



def usuarios(request):
    
    if request.method == 'GET':
        # Si se pide un dni de esta manera: usuarios?dni= <dni de alguien> se devuelve solo un usuario
        rol = request.args.get('rol')
        dni=request.args.get('dni') 
        
        # Validar si dni o rol vienen vacíos en la URL
        if dni == "":
            return jsonify({'error': 'El DNI no puede estar vacío'}), 400
        if rol == "":
            return jsonify({'error': 'El rol no puede estar vacío'}), 400
        
        
        if dni:
            usuario_dni = request.args.get('dni')
            usuario_ref = db.collection('usuarios').document(usuario_dni)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                return jsonify(usuario_doc.to_dict()), 200
            else:
                return jsonify({'error':'Usuario no encontrado'}), 400
        elif rol:
            usuario_rol = rol
            usuario_ref = db.collection('usuarios').where('rol', '==', usuario_rol).stream() 
            usuarios = [doc.to_dict() for doc in usuario_ref]
            if usuarios:
                return jsonify(usuarios), 200
            else: 
                return jsonify({'error':'No hay usuarios encontrados con ese rol'}), 400
        else:
            usuarios = [doc.to_dict() for doc in db.collection('usuarios').stream()]
            return jsonify(usuarios), 200
            
    elif request.method == 'POST':
        
        #Se piden los datos del usuario, para poder registrarlo al igual que con estudiante
        data = request.json 
        
        #se asignan los datos a las variables correspondientes 
        user_dni = data.get("dni")
        user_apellido = data.get("apellido")
        user_name = data.get("nombre")
        user_email = data.get("email")
        user_birthdate = data.get("fechaNacimiento") #firestore timeStamp
        user_registrationDate = data.get("fechaInscripcion")#firestore timeStamp
        user_username = data.get("nombreAcceso")
        user_rol = data.get('rol')
        
        #se verifica que no falte nada
        if not user_dni or not user_apellido or not user_name or not user_email or not user_rol:
            return {'Error':'Faltan datos, revise dni, nombre, apellido, correo electronico, rol'}, 400
        
        # Intenta parsear las fechas si vienen como string
        try:
            birthdate = datetime.fromisoformat(user_birthdate) if user_birthdate else None
            registration_date = datetime.fromisoformat(user_registrationDate) if user_registrationDate else None
        except ValueError:
            return {'error': 'Formato de fecha inválido'}, 400 # formato de la fecha = YYYY-mm-ddThh:mm:ss.499588
        
        try:
            #se crea el usuario usando su email como email de ingreso y su dni como su contraseña
            usuario = auth.create_user(email=user_email, password=str(user_dni))
            
            db.collection("usuarios").document(str(user_dni)).set(
                {
                    'dni':user_dni,
                    'apellido':user_apellido,
                    'nombre': user_name,
                    'email':user_email,
                    'fechaNacimiento':birthdate,
                    'fechaInscripcion':registration_date,
                    'nombreAcceso':user_username,
                    'rol':user_rol,
                    'user_uid': usuario.uid 
                }
            )
            
            
            
            return {'message': 'Usuario registrado exitosamente', 'user_id': usuario.uid}, 201
        except Exception as e:
            return {'error': str(e)}, 400
            return
    
    elif request.method == 'PUT':
        #se tiene que actualizar un usuario segun los nuevos datos que se ingresen
        data = request.json 
        
        if not data or 'dni' not in data:
            return jsonify({'error': ' Ingrese el dni del usuario correspondiente'}), 400 #######
        
        
        user_ref = db.collection('usuarios').document(data['dni'])
        user_doc = user_ref.get()
        
        #control de errores 
        if not user_doc.exists:
            return jsonify({'error': 'No se encontro el usuario especificado'}), 404
        
        if user_doc.to_dict().get('rol') == 'admin':
            return jsonify({'error': 'No se puede eliminar un usuario administrador'}), 403
        
        #se asignan los datos a las variables correspondientes 
        user_dni = data.get("dni")
        user_apellido = data.get("apellido")
        user_name = data.get("nombre")
        user_email = data.get("email")
        user_birthdate = data.get("fechaNacimiento") #firestore timeStamp
        user_registrationDate = data.get("fechaInscripcion")#firestore timeStamp
        user_username = data.get("nombreAcceso")
        user_rol = data.get('rol')
        
        
        
        
        return
    
    elif request.method == 'DELETE':
        data = request.json 
        
        if not data or 'dni' not in data:
            return jsonify({'error': ' Ingrese el dni del usuario correspondiente'}), 400 #######
        
        
        user_ref = db.collection('usuarios').document(data['dni'])
        user_doc = user_ref.get()
        
        #control de errores 
        if not user_doc.exists:
            return jsonify({'error': 'No se encontro el usuario especificado'}), 404
        
        if user_doc.to_dict().get('rol') == 'admin':
            return jsonify({'error': 'No se puede eliminar un usuario administrador'}), 403
        
        #si todo coincide : 
        
        
        #eliminacion de authentication firebase
        user_data = user_doc.to_dict() #se extraen los datos en forma de diccionario 
        user_uid = user_data.get('user_uid') #se obtiene el uid unico
        if user_uid:
            try:
                auth.delete_user(user_uid)
            except Exception as e:
                return jsonify({'error':f'No se pudo eliminar usuario:({str(e)})'}), 500
        
        #eliminacion de BD firestore
        user_ref.delete()
        return jsonify({'message':'Usuario eliminado correctamente'}), 200
    
    else:
        return jsonify({'error':'Método no permitido'}), 405   

def parsearFecha(value_date):
    try:
        final_value = datetime.fromisoformat(value_date) if value_date else None
        return final_value
    except ValueError:
            return {'error': 'Formato de fecha inválido'}, 400 # formato de la fecha = YYYY-mm-ddThh:mm:ss.499588


''' TOKEN PARA AUTENTICAR USUARIOS (faltan ROLES) DESDE EL BACKEND
id_token = request.headers.get('Authorization')
if not id_token:
    return jsonify({'error': 'Token faltante'}), 401

try:
    decoded_token = auth.verify_id_token(id_token)
    user_uid = decoded_token['uid']
    user_role = get_user_role_from_firestore(user_uid)  # tu función personalizada
except Exception as e:
    return jsonify({'error': 'Token inválido'}), 401'''