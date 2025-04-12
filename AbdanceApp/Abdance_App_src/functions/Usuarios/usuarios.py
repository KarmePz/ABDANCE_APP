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
        return
    elif request.method == 'PUT':
        return
    elif request.method == 'DELETE':
        return
    else:
        return jsonify({'error':'Método no permitido'}), 405   




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