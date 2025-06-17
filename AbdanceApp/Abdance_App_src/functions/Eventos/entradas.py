import firebase_admin
from firebase_admin import firestore
from firebase_init import db
from datetime import datetime
import qrcode
import base64
from io import BytesIO


def entradas(request, uid=None, role=None):
    if request.method == 'GET':
        return getEntradas(request)

    elif request.method == 'POST':
        return postEntrada(request)

    elif request.method == 'PUT':
        return putEntrada(request)

    elif request.method == 'DELETE':
        return {"Este metodo no esta disponible"}#deleteEntrada(request)

    else:
        return {'error': 'Método no permitido'}, 405


# GET
#@require_auth(required_roles=['admin', 'profesor'])
def getEntradas(request):
    evento_id = request.args.get('evento_id')
    entrada_id = request.args.get('entrada_id')


    if not evento_id:
        return {'error': 'Se requiere evento_id'}, 400

    ref = db.collection('eventos').document(evento_id).collection('entradas')

    if entrada_id:
        doc = ref.document(entrada_id).get()
        if doc.exists:
            return doc.to_dict(), 200
        else:
            return {'error': 'Entrada no encontrada'}, 404
    else:
        docs = ref.stream()
        entradas = [doc.to_dict() for doc in docs]
        return entradas, 200


# POST
#@require_auth(required_roles=['admin', 'profesor'])
def postEntrada(request):
    data = request.get_json()
    evento_id = data.get('evento_id')

    if not evento_id:
        return {'error': 'Se requiere evento_id'}, 400

    entrada_data = {
        'nombre': data.get('nombre'),
        'apellido': data.get('apellido'),
        'dni': data.get('dni'),
        'email': data.get('email'),
        'telefono': data.get('telefono'),
        'tipo_entrada': data.get('tipo_entrada'),
        'precio': data.get('precio'),
        'estado': 'activa',
        'created_at': datetime.now().isoformat()
    }

    # Crear entrada y generar ID
    ref = db.collection('eventos').document(evento_id).collection('entradas').document()
    entrada_data['id'] = ref.id

    # Generar código QR con el ID de la entrada
    qr = qrcode.make(ref.id)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    entrada_data['qr_code'] = qr_base64

    # Guardar en Firestore
    ref.set(entrada_data)

    return {'mensaje': 'Entrada creada correctamente', 'entrada': entrada_data}, 201


# PUT: Cambiar solo el estado de una entrada

def putEntrada(request):
    data = request.get_json()
    evento_id = data.get('evento_id')
    entrada_id = data.get('entrada_id')
    nuevo_estado = data.get('estado')

    if not evento_id or not entrada_id or not nuevo_estado:
        return {'error': 'Faltan datos'}, 400

    ref = db.collection('eventos').document(evento_id).collection('entradas').document(entrada_id)
    ref.update({'estado': nuevo_estado})
    return {'mensaje': 'Estado de entrada actualizado'}, 200


# DELETE: 
"""
def deleteEntrada(request):
    evento_id = request.args.get('evento_id')
    entrada_id = request.args.get('entrada_id')

    if not evento_id or not entrada_id:
        return {'error': 'Faltan datos'}, 400

    ref = db.collection('eventos').document(evento_id).collection('entradas').document(entrada_id)
    ref.delete()
    return {'mensaje': 'Entrada eliminada'}, 200
"""