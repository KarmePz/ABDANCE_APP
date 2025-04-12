from flask import Flask, request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime






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
    return
