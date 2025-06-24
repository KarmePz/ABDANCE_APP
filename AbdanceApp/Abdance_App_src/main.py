import functions_framework 
##from flask import Flask, jsonify, request
from util.cors import apply_cors, apply_cors_manual

import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth

from functions.Asistencias.asistencias import (
    inasistencias, 
    registrar_inasistencia
)
from functions.Cuotas.cuotas import (
    cuotas, 
    getCuotasDNIAlumno,
    pagar_cuota, 
    pagar_cuotas_manualmente,
    crear_cuotas_mes,
    eliminar_cuotas_mes
)
from functions.Estadisticas.estadisticas import (
    total_pagado_mes,
    totales_por_mes_anio
)
from functions.Cuotas.pagos import crear_preferencia_cuota
from functions.Usuarios.auth_users import register_student
from functions.Usuarios.usuarios import eliminar_usuario_con_inscripciones, usuarios
from functions.Eventos.eventos import eventos
from functions.Disciplinas.disciplinas import disciplinas, gestionarAlumnosDisciplina
from functions.Eventos.entradas import _process_mercadopago_notification_task, entradas, webhook_mercadopago_processor
from functions.Eventos.crear_preferencia import crear_preferencia
#from functions.Eventos.entradas import guardarFormularioTemporal

# #funciones 
# from functions.Asistencias.asistencias import inasistencias
# from functions.Cuotas.pagos import cuotas
# from functions.Usuarios.auth_users import register_student
# from functions.Asistencias.asistencias import registrar_inasistencia
# from functions.Usuarios.usuarios import usuarios
# from functions.Eventos.eventos import eventos
# from functions.Disciplinas.disciplinas import disciplinas

# Si no existe una app firebase la crea con las credenciales automáticas de Google Cloud
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

@functions_framework.http
def main(request):
    # Configuración básica de CORS para peticiones OPTIONS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': 'https://abdance-app-frontend-epu45bv2q-camilos-projects-fd28538a.vercel.app',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        return ('', 204, headers)
    
    # url y método de la request
    path = request.path
    method = request.method
    
    # Router de endpoints
    if path == '/' and method == 'GET':
        return 'Hola Main View', 200 
    elif path == '/cuotas':
        return apply_cors(cuotas(request))
    elif path == '/cuotas/alumno':
        return apply_cors(getCuotasDNIAlumno(request))
    elif path == "/crear_preferencia_cuota":
        return apply_cors(crear_preferencia_cuota(request))
    elif path == "/pagar_cuota":
        return apply_cors(pagar_cuota(request))
    elif path == "/pagar_cuota/manual":
        return apply_cors(pagar_cuotas_manualmente(request))
    elif path == "/crear-cuotas-mes":
        return apply_cors(crear_cuotas_mes(request))
    elif path == "/eliminar-cuotas-mes":
        return apply_cors(eliminar_cuotas_mes(request))
    elif path == "/estadisticas/total-del-mes":
        return apply_cors(total_pagado_mes(request))
    elif path == "/estadisticas/totales-por-anio":
        return apply_cors(totales_por_mes_anio(request))
    elif path == '/eventos':
        return apply_cors_manual(eventos(request))
    elif path == '/entradas':
        return apply_cors_manual(entradas(request))
    elif path == '/crear_preferencia':
        return apply_cors_manual(crear_preferencia(request))
    elif path == '/api/registrar_entradas':
        return apply_cors_manual(entradas(request))
    # elif path == '/formularios-temporales':
    #     return apply_cors_manual(guardarFormularioTemporal(request))
    elif path == '/webhook/mercadopago' and method == 'POST':
        # No aplicamos CORS aquí, ya que Mercado Pago es quien hace la llamada.
        # La función 'webhook_mercadopago_processor' ya contendrá la lógica de validación
        return webhook_mercadopago_processor(request)
    
    elif path == "/tasks/mercadopago-processor" and method == "POST":
        return _process_mercadopago_notification_task(request)

    
    elif path == '/usuarios/register-student':
        return apply_cors(register_student(request)) 
    elif path == '/usuarios':
        return usuarios(request)
    elif path == "/usuarios/eliminar" and method == "DELETE":
        return apply_cors(eliminar_usuario_con_inscripciones(request))
    elif path == '/inasistencias':
        return apply_cors(inasistencias(request))
    elif path =='/disciplinas/gestionar-alumnos':
        return apply_cors(gestionarAlumnosDisciplina(request)) 
    elif path == '/asistencias/registrar':
        return apply_cors(registrar_inasistencia(request))
    elif path == '/disciplinas':
        return disciplinas(request)
    elif path == '/disciplinas/alumno':
        return apply_cors(gestionarAlumnosDisciplina(request))
        # se debe agregar, modificar, eliminar,y ver datos de un alumno de un profesor según su dni
    else:
        return 'Method not allowed', 405

# --- Comentarios sobre lo que modifiqué / quitado ---

"""
# Comenté todo este bloque porque en Cloud Functions NO debe haber código
# que levante el servidor explícitamente (ejecutar app.run o run_simple).
# GCP maneja eso automáticamente y sólo necesita la función decorada con @functions_framework.http.

# --- Ejecutar localmente si hace falta (NO interfiere con Cloud Functions) ---
"""
if __name__ == "__main__":
    from flask import Flask, request
    import logging
    from werkzeug.serving import run_simple

    logging.basicConfig(level=logging.DEBUG)

    flask_app = Flask(__name__)

    @flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    @flask_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def catch_all(path):
        try:
            return main(request)
        except Exception as e:
            flask_app.logger.error(f"Error interno: {e}", exc_info=True)
            return "Error interno en el servidor", 500

    # GCP espera que escuche en el puerto 8080
    import os
    port = int(os.environ.get("PORT", 8080))
    run_simple('0.0.0.0', port, flask_app, use_debugger=True, use_reloader=True)


# --- Fin de comentarios ---
