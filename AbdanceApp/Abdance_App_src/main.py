import functions_framework 
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, auth
#funciones 
from functions.Asistencias.asistencias import asistencias
from functions.Cuotas.pagos import cuotas
from functions.Usuarios.auth_users import register_student
from functions.Usuarios.usuarios import usuarios
from functions.Eventos.eventos import eventos


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
    
    
    
    if path == '/' and method == 'GET':
        return 'Hola Main View', 200 
    elif path == '/asistencias':
        return asistencias(request) 
    elif path == '/cuotas':
        return cuotas(request) 
    elif path == '/eventos':
        return eventos(request) 
    elif path == '/usuarios/register-student':
        return register_student(request) 
    elif path == '/usuarios':
        return usuarios(request)
    else:
        return 'Method not allowed', 405