import functions_framework 
##from flask import Flask, jsonify, request



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
from functions.Disciplinas.disciplinas import disciplinas
from functions.Eventos.entradas import entradas
from functions.Eventos.crear_preferencia import crear_preferencia


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
            'Access-Control-Allow-Origin': '*',
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
    elif path == '/entradas':
        return entradas(request)
    elif path == '/crear_preferencia':
        return crear_preferencia(request)
    elif path == '/usuarios/register-student':
        return register_student(request) 
    elif path == '/usuarios' and method == 'GET':
        return usuarios(request)
    elif path == '/inasistencias':
        return inasistencias(request) 
    elif path == '/asistencias/registrar':
        return registrar_inasistencia(request)
    elif path == '/disciplinas':
        return disciplinas(request)
    elif path == '/disciplinas/alumno':
        return ('Endpoint en construcción', 501)#se debe agregar, modificar, eliminar,y ver datos de un alumno de una disciplina segun su dni
    elif path == '/disciplinas/horario':
        return ('Endpoint en construcción', 501)#se debe agregar, modificar, eliminar,y ver datos de un horarios de una disciplina segun su id
    elif path == '/disciplinas/profesor':
        return ('Endpoint en construcción', 501) #se debe agregar, modificar, eliminar,y ver datos de un alumno de un profesor segun su dni
    else:
        return 'Method not allowed', 405
    

if __name__ == '__main__':
    from flask import Flask, request
    from werkzeug.serving import run_simple
    from flask_cors import CORS

    import logging
    logging.basicConfig(level=logging.DEBUG)

    flask_app = Flask(__name__)
    CORS(flask_app) 
    
    @flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    @flask_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def catch_all(path):
        try:
            return main(request)
        except Exception as e:
            # Esto imprime el error en la consola
            flask_app.logger.error(f"Error interno: {e}", exc_info=True)
            return "Error interno en el servidor", 500

    run_simple('127.0.0.1', 5000, flask_app, use_debugger=True, use_reloader=True)

