import functions_framework 
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, auth
#funciones 
from functions.Asistencias.asistencias import asistencias
from functions.Cuotas.pagos import cuotas
from functions.Usuarios.auth_users import register_student
from functions.Asistencias.asistencias import registrar_inasistencia
from functions.Usuarios.usuarios import usuarios
from functions.Eventos.eventos import eventos
from functions.Disciplinas.disciplinas import disciplinas


app = Flask(__name__)

#si no existe una app firebase la crea con las credenciales automaticas de Google Cloud
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

@functions_framework.http
def main(request):
    
    #url y metodo de la request
    path = request.path
    method = request.method
    
    
    #metodos y rutas
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
    elif path == '/asistencias':
        return asistencias(request) 
    elif path == '/asistencias/registrar':
        return registrar_inasistencia(request)
    elif path == '/disciplinas':
        return disciplinas(request)
    elif path == '/disciplinas/alumno':
        return ##TODO #se debe agregar, modificar, eliminar,y ver datos de un alumno de una disciplina segun su dni
    elif path == '/disciplinas/horario':
        return ##TODO #se debe agregar, modificar, eliminar,y ver datos de un horarios de una disciplina segun su id
    elif path == '/disciplinas/profesor':
        return ##TODO #se debe agregar, modificar, eliminar,y ver datos de un alumno de un profesor segun su dni
    else:
        return 'Method not allowed', 405