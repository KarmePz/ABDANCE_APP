import json
import functions_framework
import firebase_admin
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from functions.Usuarios.auth_decorator import require_auth

