import functions_framework 
from flask import Flask, jsonify, request
#funciones 
from functions.Asistencias.asistencias import asistencias
from functions.Cuotas.pagos import cuotas
from functions.Usuarios.auth_users import usuarios
from functions.Eventos.eventos import eventos

@functions_framework.http
def main(request):
    
    #url y metodo de la request
    path = request.path
    method = request.method
    
    
    
    if path == '/' and method == 'GET':
        return 'Hola Main View', 200 
    elif path == '/asistencias' and method == 'GET':
        return asistencias(request) 
    elif path == '/cuotas' and method == 'GET':
        return cuotas(request) 
    elif path == '/eventos' and method == 'GET':
        return eventos(request) 
    elif path == '/usuarios' and method == 'GET':
        return usuarios(request) 
    else:
        return 'Method not allowed', 405