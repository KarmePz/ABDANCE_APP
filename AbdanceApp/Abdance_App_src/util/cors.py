from flask import jsonify, make_response


# def apply_cors(response_tuple):
#     # headers = {
#     #     'Access-Control-Allow-Origin': 'http://localhost:5173',  # o '*' para todos
#     #     'Access-Control-Allow-Headers': 'Content-Type, Authorization',
#     #     'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
#     # }
#     data, status = response_tuple
#     response = make_response(jsonify(data), status)
#     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
#     return response
#     # return (response_body, status, headers)

from flask import Flask, request, make_response
from flask_cors import CORS

app = Flask(__name__)

ALLOWED_ORIGINS = [
    "https://abdance-app-frontend-37vdurqtt-camilos-projects-fd28538a.vercel.app"
]


# def apply_cors(response):
#     origin = request.headers.get("Origin")
#     if origin in ALLOWED_ORIGINS:
#         response.headers["Access-Control-Allow-Origin"] = origin
#         response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
#         response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
#     return response

def apply_cors(response_tuple):
    data, status = response_tuple
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = 'https://abdance-app-frontend-37vdurqtt-camilos-projects-fd28538a.vercel.app'
    return response

from flask import make_response

def apply_cors_manual(response_tuple):
    """
    Aplica CORS a una respuesta manualmente cuando no es interceptada correctamente por @after_request.
    """
    if isinstance(response_tuple, tuple):
        data, status = response_tuple
        response = make_response(data, status)
    else:
        response = make_response(response_tuple)

    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"

    if origin and "ngrok-free.app" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin

    csp = (
        "default-src 'self' https://cdn.ngrok.com 'unsafe-eval' 'unsafe-inline'; "
        "font-src 'self' https://assets.ngrok.com;"
    )
    response.headers['Content-Security-Policy'] = csp

    return response
