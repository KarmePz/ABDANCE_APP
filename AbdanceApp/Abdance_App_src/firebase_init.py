
import firebase_admin
from firebase_admin import credentials, firestore, auth

if not firebase_admin._apps:
    # cred = credentials.Certificate('../serviceKey.json') ###Esta linea es para pruebas locales
    cred = credentials.ApplicationDefault()###Esta linea es para produccion
    firebase_admin.initialize_app(cred)

# Exponer Firestore y Auth para reutilizar
db = firestore.client()