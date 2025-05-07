from flask import Flask, request, jsonify, Response
import json
import functions_framework
import firebase_admin
import mercadopago
import os
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv



def cuotas(request):
    return 'hola pagos', 200


def efectuar_pago(request):
    #Obtiene los datos del .env
    load_dotenv()
    PROD_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN_TEST")

    mercado_pago_sdk = mercadopago.SDK(str(PROD_ACCESS_TOKEN))

    return str(PROD_ACCESS_TOKEN), 200 