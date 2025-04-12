
import firebase_admin
from firebase_admin import credentials, firestore, auth

if not firebase_admin._apps:
    cred = credentials.Certificate('../serviceKey.json')
    firebase_admin.initialize_app(cred)

# Exponer Firestore y Auth para reutilizar
db = firestore.client()