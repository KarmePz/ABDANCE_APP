import functions_framework 
##from flask import Flask, jsonify, request
from util.cors import apply_cors


import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth


from functions.Asistencias.asistencias import (
    inasistencias, 
    registrar_inasistencia
)
from functions.Cuotas.pagos import cuotas
from functions.Usuarios.auth_users import register_student
from functions.Usuarios.usuarios import usuarios
from functions.Eventos.eventos import eventos
from functions.Disciplinas.disciplinas import disciplinas, gestionarAlumnosDisciplina


# #funciones 
# from functions.Asistencias.asistencias import inasistencias
# from functions.Cuotas.pagos import cuotas
# from functions.Usuarios.auth_users import register_student
# from functions.Asistencias.asistencias import registrar_inasistencia
# from functions.Usuarios.usuarios import usuarios
# from functions.Eventos.eventos import eventos
# from functions.Disciplinas.disciplinas import disciplinas



#si no existe una app firebase la crea con las credenciales automaticas de Google Cloud
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)



@functions_framework.http
def main(request):
    # Configuración básica de CORS para peticiones OPTIONS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': 'http://localhost:5173',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)
    #url y metodo de la request
    path = request.path
    method = request.method
    
    
    # Router de endpoints
    if path == '/' and method == 'GET':
        return 'Hola Main View', 200 
    elif path == '/cuotas':
        return cuotas(request)
    elif path == '/eventos':
        return eventos(request) 
    elif path == '/usuarios/register-student':
        return register_student(request) 
    elif path == '/usuarios':
        return usuarios(request)
    elif path == '/inasistencias':
        return inasistencias(request) 
    elif path == '/asistencias/registrar':
        return apply_cors(registrar_inasistencia(request))
    elif path == '/disciplinas':
        return disciplinas(request)
    elif path == '/disciplinas/alumno':
        return gestionarAlumnosDisciplina(request)
        return ('Endpoint en construcción', 501)#se debe agregar, modificar, eliminar,y ver datos de un alumno de una disciplina segun su dni
    elif path == '/disciplinas/horario':
        return ('Endpoint en construcción', 501)#se debe agregar, modificar, eliminar,y ver datos de un horarios de una disciplina segun su id
    elif path == '/disciplinas/profesor':
        return ('Endpoint en construcción', 501) #se debe agregar, modificar, eliminar,y ver datos de un alumno de un profesor segun su dni
    else:
        return 'Method not allowed', 405
    

