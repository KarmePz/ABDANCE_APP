import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore
from firebase_init import db
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from email.message import EmailMessage
import smtplib
from flask import request

# Cargar variables de entorno
load_dotenv()

def entradas(req, uid=None, role=None):
    if req.method == 'GET':
        if req.path.endswith('/formulario_temporal'):
            return getFormularioTemporal(req)
        return getEntradas(req)

    elif req.method == 'POST':
        if req.path.endswith('/guardar_formulario_temporal'):
            return guardarFormularioTemporal(req)

        try:
            data = req.get_json()
            if 'formularios' in data:
                return postEntradasMultiples(req)
            else:
                return postEntrada(req)
        except Exception as e:
            return {'error': str(e)}, 500

    elif req.method == 'PUT':
        return putEntrada(req)

    elif req.method == 'DELETE':
        return {"Este metodo no esta disponible"}

    else:
        return {'error': 'Método no permitido'}, 405

# ----------------------------------------------------------------------
# GET Entradas
# ----------------------------------------------------------------------

def getEntradas(req):
    evento_codigo = req.args.get('evento_id')  # sigue usando evento_id como query param

    if not evento_codigo:
        return {'error': 'Se requiere evento_id'}, 400

    # Buscar el evento por código
    eventos_ref = db.collection('eventos')
    query = eventos_ref.where('codigo', '==', evento_codigo).stream()
    evento_docs = list(query)

    if not evento_docs:
        return {'error': 'Evento no encontrado'}, 404

    evento_doc = evento_docs[0]
    ref_entradas = eventos_ref.document(evento_doc.id).collection('entradas')
    docs = ref_entradas.stream()
    entradas = [doc.to_dict() for doc in docs]
    return entradas, 200


# ----------------------------------------------------------------------
# POST: Guardar Formulario Temporal (antes del pago)
# ----------------------------------------------------------------------

def guardarFormularioTemporal(req):
    try:
        data = req.get_json()
        evento_id = data.get('evento_id')
        formularios = data.get('formularios')
        entradas = data.get('entradas')

        if not evento_id or not formularios or not entradas:
            return {'error': 'Faltan datos'}, 400

        doc_ref = db.collection('formularios_temporales').document()
        doc_data = {
            'id': doc_ref.id,
            'evento_id': evento_id,
            'formularios': formularios,
            'entradas': entradas,
            'estado': 'pendiente',
            'created_at': datetime.now().isoformat()
        }
        doc_ref.set(doc_data)

        return {'formId': doc_ref.id}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# ----------------------------------------------------------------------
# GET: Obtener Formulario Temporal por ID
# ----------------------------------------------------------------------

def getFormularioTemporal(req):
    form_id = req.args.get('form_id')

    if not form_id:
        return {'error': 'Se requiere form_id'}, 400

    doc_ref = db.collection('formularios_temporales').document(form_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict(), 200
    else:
        return {'error': 'Formulario no encontrado'}, 404

# ----------------------------------------------------------------------
# POST: Entrada individual
# ----------------------------------------------------------------------

def postEntrada(req):
    data = req.get_json()
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

    ref = db.collection('eventos').document(evento_id).collection('entradas').document()
    entrada_data['id'] = ref.id

    qr = qrcode.make(ref.id)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    entrada_data['qr_code'] = qr_base64

    ref.set(entrada_data)

    return {'mensaje': 'Entrada creada correctamente', 'entrada': entrada_data}, 201

# ----------------------------------------------------------------------
# PUT: Actualizar estado
# ----------------------------------------------------------------------

def putEntrada(req):
    data = req.get_json()
    evento_id = data.get('evento_id')
    entrada_id = data.get('entrada_id')
    nuevo_estado = data.get('estado')

    if not evento_id or not entrada_id or not nuevo_estado:
        return {'error': 'Faltan datos'}, 400

    ref = db.collection('eventos').document(evento_id).collection('entradas').document(entrada_id)
    ref.update({'estado': nuevo_estado})
    return {'mensaje': 'Estado de entrada actualizado'}, 200

# ----------------------------------------------------------------------
# POST múltiple con envío de mails
# ----------------------------------------------------------------------

def postEntradasMultiples(req):
    data = req.get_json()
    evento_id = data.get("evento_id")
    formularios = data.get("formularios")

    if not evento_id or not formularios:
        return {'error': 'Faltan datos'}, 400

    entradas_creadas = []

    MAIL_USER = os.getenv("MAIL_USER")
    MAIL_PASS = os.getenv("MAIL_PASS")
    MAIL_FROM = os.getenv("MAIL_FROM")

    if not MAIL_USER or not MAIL_PASS or not MAIL_FROM:
        return {'error': 'Configuración de correo no definida en variables de entorno'}, 500

    for f in formularios:
        ref = db.collection('eventos').document(evento_id).collection('entradas').document()

        entrada_data = {
            'id': ref.id,
            'nombre': f.get('nombre'),
            'apellido': f.get('apellido'),
            'dni': f.get('dni'),
            'email': f.get('email'),
            'telefono': f.get('telefono'),
            'tipo_entrada': f.get('tipo'),
            'estado': 'activa',
            'created_at': datetime.now().isoformat()
        }

        qr = qrcode.make(ref.id)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        entrada_data['qr_code'] = qr_base64

        ref.set(entrada_data)
        entradas_creadas.append(entrada_data)

        # Envío de email
        try:
            msg = EmailMessage()
            msg['Subject'] = f"Entrada para el evento"
            msg['From'] = MAIL_FROM
            msg['To'] = entrada_data['email']
            msg.set_content(f"""
Hola {entrada_data['nombre']} {entrada_data['apellido']},

Gracias por tu compra. Esta es tu entrada al evento.

DNI: {entrada_data['dni']}
Tipo de Entrada: {entrada_data['tipo_entrada']}
ID de Entrada: {entrada_data['id']}
""")
            img_data = base64.b64decode(qr_base64)
            msg.add_attachment(img_data, maintype='image', subtype='png', filename="entrada_qr.png")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(MAIL_USER, MAIL_PASS)
                smtp.send_message(msg)
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return {'mensaje': 'Entradas registradas y correos enviados', 'entradas': entradas_creadas}, 201
