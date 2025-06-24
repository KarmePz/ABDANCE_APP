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
from flask import request, jsonify
import mercadopago
import json
import logging
from google.cloud import tasks_v2 # ✅ Importar Cloud Tasks SDK

# Cargar variables de entorno
load_dotenv()

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables de entorno
MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET")
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_USER = os.getenv("MAIL_USER")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID") # Tu ID de proyecto de GCP
GCP_LOCATION = os.getenv("GCP_LOCATION") # La región de tu Cloud Function (ej. us-central1)
GCP_QUEUE_NAME = os.getenv("GCP_QUEUE_NAME", "mercadopago-notifications") # Nombre de la cola de tareas


# Inicializar el SDK de Mercado Pago
sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

try:
    task_client = tasks_v2.CloudTasksClient()

except Exception as e:
    logger.error(f"Error inicializando CloudTasksClient globalmente: {e}")


def entradas(req, uid=None, role=None):
    if req.method == 'GET':
        return getEntradas(req)

    # El POST de entradas ya no se usará directamente para la creación,
    # sino que se hará a través de la función que procesa el webhook.
    elif req.method == 'POST':
        return jsonify({"error": "Este método POST no está disponible directamente. Las entradas se crean vía webhook de Mercado Pago."}), 405
    elif req.method == 'PUT':
        return putEntrada(req)

    elif req.method == 'DELETE':
        return jsonify({"error": "Este método DELETE no está disponible"}), 405

    else:
        return jsonify({'error': 'Método no permitido'}), 405

# --- Funciones Existentes (No se modifican si no es necesario) ---

def getEntradas(req):
    evento_codigo = req.args.get('evento_id')

    if not evento_codigo:
        return jsonify({'error': 'Se requiere evento_id'}), 400

    eventos_ref = db.collection('eventos')
    query = eventos_ref.where('codigo', '==', evento_codigo).stream()
    evento_docs = list(query)

    if not evento_docs:
        return jsonify({'error': 'Evento no encontrado'}), 404

    evento_doc = evento_docs[0]
    ref_entradas = eventos_ref.document(evento_doc.id).collection('entradas')
    docs = ref_entradas.stream()
    entradas = [doc.to_dict() for doc in docs]
    return jsonify(entradas), 200

def putEntrada(req):
    data = req.get_json()
    evento_id = data.get('evento_id')
    entrada_id = data.get('entrada_id')
    nuevo_estado = data.get('estado')

    if not evento_id or not entrada_id or not nuevo_estado:
        return jsonify({'error': 'Faltan datos'}), 400

    ref = db.collection('eventos').document(evento_id).collection('entradas').document(entrada_id)
    ref.update({'estado': nuevo_estado})
    return jsonify({'mensaje': 'Estado de entrada actualizado'}), 200

# --- Nuevas Funciones para el Webhook y Procesamiento ---

from google.api_core.exceptions import PermissionDenied
from google.api_core.exceptions import InvalidArgument

def webhook_mercadopago_processor(request):
    logger.info("📩 Webhook de Mercado Pago recibido.") 
    
    # --- Headers y cuerpo para debug ---
    logger.info(f"Headers del webhook: {request.headers}")
    try:
        raw_body = request.get_data(as_text=True)
        logger.info(f"Cuerpo RAW del webhook: {raw_body}")
    except Exception as e:
        logger.warning(f"No se pudo leer el cuerpo RAW: {e}")

    # --- Validación inicial de headers ---
    try:
        mp_request_id = request.headers.get('x-request-id')
        if not mp_request_id:
            logger.warning("❗ Faltante X-Request-Id en webhook.")
    except Exception as e:
        logger.error(f"❌ Error en validación inicial: {e}", exc_info=True)
        return jsonify({'message': 'Internal Server Error during validation'}), 500

    # --- Parsear datos del webhook ---
    topic = None
    resource_id = None
    webhook_data = {}
    try:
        webhook_data = request.get_json(silent=True)
        if webhook_data:
            logger.info(f"Cuerpo JSON: {webhook_data}")
            topic = webhook_data.get('topic')
            if 'data' in webhook_data and isinstance(webhook_data['data'], dict):
                resource_id = webhook_data['data'].get('id')
            elif 'resource' in webhook_data:
                resource_id = webhook_data.get('resource')

            if not topic and 'type' in webhook_data:
                topic = webhook_data.get('type')
            if not resource_id and 'id' in webhook_data:
                resource_id = webhook_data.get('id')
    except Exception as e:
        logger.warning(f"⚠️ Error al parsear JSON. Usando query params. {e}")

    # --- Fallback con query params ---
    if not topic:
        topic = request.args.get('topic')
    if not resource_id:
        resource_id = request.args.get('id')

    if not resource_id and request.args.get('data.id') and request.args.get('type') == 'payment':
        resource_id = request.args.get('data.id')
        topic = request.args.get('type')

    if resource_id and isinstance(resource_id, str) and '/' in resource_id:
        try:
            resource_id = resource_id.split('/')[-1]
            logger.info(f"ID extraído de URL: {resource_id}")
        except Exception as e:
            logger.error(f"Error extrayendo ID de URL: {e}")
            resource_id = None

    if not topic or not resource_id:
        logger.error(f"❌ Webhook sin topic o ID válido. Query: {request.args}, JSON: {webhook_data}")
        return jsonify({'message': 'Missing topic or ID'}), 400

    logger.info(f"✅ Procesando webhook: topic={topic}, resource_id={resource_id}")

    logger.info(f"[CloudTasks] project_id={project_id}, location_id={location_id}, queue_name={queue_name}")
    # --- Encolar la tarea ---
    try:
        project_id = os.getenv('GCP_PROJECT_ID')
        location_id = os.getenv('GCP_LOCATION')
        queue_name = os.getenv('GCP_QUEUE_NAME')

        if not all([project_id, location_id, queue_name]):
            logger.error("❌ Variables de entorno faltantes para Cloud Tasks.")
            return jsonify({"status": "Error: configuración incompleta de Cloud Tasks"}), 500

        local_task_client = tasks_v2.CloudTasksClient()
        parent = local_task_client.queue_path(project_id, location_id, queue_name)

        payload = {
            'topic': topic,
            'resource_id': resource_id,
            'full_payload': webhook_data
        }

        task_target_url = f"https://{location_id}-{project_id}.cloudfunctions.net/main/tasks/mercadopago-processor"

        task = {
            'http_request': {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': task_target_url,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(payload).encode('utf-8'),
                'oidc_token': {
                    'service_account_email': f'{project_id}@appspot.gserviceaccount.com'
                }
            }
        }

        response = local_task_client.create_task(parent=parent, task=task)
        logger.info(f"✅ Tarea encolada correctamente: {response.name}")
        return jsonify({"message": "Notification enqueued", "task_name": response.name}), 200

    except PermissionDenied as e:
        logger.error("❌ Permiso denegado al crear la tarea en Cloud Tasks. Verifica organización y región.", exc_info=True)
        return jsonify({"error": "Permission denied on Cloud Tasks (verifica organización y GCP_LOCATION)"}), 500

    except InvalidArgument as e:
        logger.error("❌ Argumento inválido al crear la tarea. Verifica configuración y URL.", exc_info=True)
        return jsonify({"error": "Invalid arguments for Cloud Tasks"}), 500

    except Exception as e:
        logger.error(f"❌ Error inesperado en la encolación de tarea: {e}", exc_info=True)
        return jsonify({'message': 'Internal error while enqueuing'}), 500


def _process_mercadopago_notification_task(request):
    """
    Función que se ejecuta de forma asíncrona para procesar la notificación de Mercado Pago.
    Esta función es el 'worker' y es el objetivo de la tarea de Cloud Tasks.
    """
    logger.info("Iniciando procesamiento asíncrono de notificación de Mercado Pago.")
    try:
        data = request.get_json()
        topic = data.get('topic')
        resource_id = data.get('resource_id')
        full_payload = data.get('full_payload') # El payload original de MP
        
        if not topic or not resource_id:
            logger.error(f"Payload de tarea incompleto: {data}")
            return jsonify({'error': 'Missing topic or resource_id in task payload'}), 400

        merchant_order_data = None

        if topic == 'payment':
            logger.info(f"Procesando notificación de pago para ID: {resource_id}")
            # Obtener el pago completo
            payment_response = sdk.payment().get(resource_id)
            if 'response' not in payment_response:
                logger.error(f"No se pudo obtener el pago {resource_id}: {payment_response}")
                # Lanzar excepción para que Cloud Tasks reintente
                raise Exception(f"Failed to get payment {resource_id}")
            
            payment_data = payment_response['response']
            
            # Obtener la external_reference del pago (contiene evento_id y form_id)
            external_reference = payment_data.get('external_reference')
            if not external_reference:
                logger.error(f"Pago {resource_id} sin external_reference. No se puede vincular la orden.")
                return jsonify({'error': 'Payment missing external_reference'}), 400
            
            # La external_reference es "evento_id___form_id"
            try:
                evento_id, form_id = external_reference.split('___')
            except ValueError:
                logger.error(f"Formato de external_reference inválido: {external_reference}")
                return jsonify({'error': 'Invalid external_reference format'}), 400

            # Obtener la merchant_order a través del payment
            merchant_order_id = payment_data.get('order', {}).get('id') # ID de la merchant_order asociada al pago
            
            if merchant_order_id:
                logger.info(f"Obteniendo merchant_order {merchant_order_id} para pago {resource_id}")
                merchant_order_response = sdk.merchant_orders().get(merchant_order_id)
                if 'response' not in merchant_order_response:
                    logger.error(f"No se pudo obtener merchant_order {merchant_order_id}: {merchant_order_response}")
                    raise Exception(f"Failed to get merchant_order {merchant_order_id}")
                merchant_order_data = merchant_order_response['response']
            else:
                logger.warning(f"Pago {resource_id} no tiene merchant_order asociada. Intentando con preferencia.")
                
                return jsonify({'error': 'Payment has no associated merchant_order.'}), 400


        elif topic == 'merchant_order':
            logger.info(f"Procesando notificación de merchant_order para ID: {resource_id}")
            # Obtener la merchant_order directamente
            merchant_order_response = sdk.merchant_orders().get(resource_id)
            if 'response' not in merchant_order_response:
                logger.error(f"No se pudo obtener merchant_order {resource_id}: {merchant_order_response}")
                raise Exception(f"Failed to get merchant_order {resource_id}")
            merchant_order_data = merchant_order_response['response']
            
            # Obtener la external_reference de la merchant_order
            external_reference = merchant_order_data.get('external_reference')
            if not external_reference:
                logger.error(f"Merchant order {resource_id} sin external_reference. No se puede vincular.")
                return jsonify({'error': 'Merchant order missing external_reference'}), 400
            
            try:
                evento_id, form_id = external_reference.split('___')
            except ValueError:
                logger.error(f"Formato de external_reference inválido en merchant_order: {external_reference}")
                return jsonify({'error': 'Invalid external_reference format for merchant_order'}), 400

        else:
            logger.info(f"Tipo de topic '{topic}' no manejado.")
            return jsonify({'message': f'Topic {topic} not processed.'}), 200

        if not merchant_order_data:
            logger.error("No se pudo obtener la merchant_order para procesar.")
            return jsonify({'error': 'Could not retrieve merchant order data'}), 500

        # ✅ Lógica de validación de pagos (TU LÓGICA PRINCIPAL)
        total_approved_amount = 0
        for payment in merchant_order_data.get('payments', []):
            if payment.get('status') == 'approved':
                total_approved_amount += float(payment.get('transaction_amount', 0))
        
        order_total_amount = float(merchant_order_data.get('total_amount', 0))

        logger.info(f"Merchant Order {merchant_order_data['id']}: Total aprobado {total_approved_amount}, Total orden {order_total_amount}")

        if total_approved_amount >= order_total_amount:
            logger.info(f"Pago de la Merchant Order {merchant_order_data['id']} completado. Procediendo a crear entradas.")
            
            # 1. Obtener datos de los compradores y entradas solicitadas del temporal
            form_temporal_doc_ref = db.collection("formularios_pendientes_pago").document(form_id)
            form_temporal_doc = form_temporal_doc_ref.get()

            if not form_temporal_doc.exists:
                logger.error(f"Datos de formulario temporal {form_id} no encontrados. No se pueden crear entradas.")
                return jsonify({'error': 'Temporary form data not found'}), 500
            
            form_data = form_temporal_doc.to_dict()
            datos_compradores = form_data.get('datos_compradores', [])
            entradas_solicitadas = form_data.get('entradas_solicitadas', [])
            
            # 2. Crear las entradas finales en Firestore y enviar emails
            _crear_entradas_finales_y_enviar_email(
                evento_id, 
                datos_compradores, 
                entradas_solicitadas, 
                merchant_order_data # Pasa la merchant_order completa para info de pago
            )
            
            # 3. Limpiar el registro temporal
            form_temporal_doc_ref.delete()
            logger.info(f"Registro temporal {form_id} eliminado.")

            return jsonify({'message': 'Payment approved, entries created and email sent'}), 200
        else:
            logger.info(f"Pago de la Merchant Order {merchant_order_data['id']} NO completado (faltan {order_total_amount - total_approved_amount}).")
            # Aquí podrías manejar estados "pending", "partially_paid", etc.
            # Por ahora, simplemente no creamos la entrada final.
            return jsonify({'message': 'Payment not fully approved yet or still pending'}), 200

    except Exception as e:
        logger.error(f"Error procesando notificación de Mercado Pago en worker: {e}", exc_info=True)
        # Lanzar excepción para que Cloud Tasks reintente la tarea
        raise # Vuelve a lanzar para que Cloud Tasks lo maneje

# Función para crear entradas finales en Firestore, generar QR y enviar email
def _crear_entradas_finales_y_enviar_email(evento_id, datos_compradores, entradas_solicitadas, merchant_order_data):
    """
    Crea las entradas en Firestore, genera los QR y envía emails.
    Esta función ahora es asíncrona para permitir el envío de email sin bloquear.
    """
    logger.info(f"Creando entradas finales para evento {evento_id} y {len(datos_compradores)} compradores.")
    
    evento_ref = db.collection("eventos").document(evento_id)
    evento_doc = evento_ref.get()
    if not evento_doc.exists:
        logger.error(f"Evento {evento_id} no encontrado para crear entradas finales.")
        raise Exception("Evento no encontrado al crear entradas finales.")
    
    evento_data = evento_doc.to_dict()
    nombre_evento = evento_data.get("nombre", "Evento Desconocido")
    
    # Mapeo de entradas solicitadas a sus precios para referencia
    precios_entradas = {e["tipo"]: e["precio"] for e in entradas_solicitadas}

    for idx, comprador_data in enumerate(datos_compradores):
        

        # Asumiendo que `datos_compradores` ya tiene el `tipo_entrada` asociado por el frontend:
        tipo_entrada = comprador_data.get('tipo_entrada') # El frontend debería enviar esto!
        if not tipo_entrada:
            # Si el frontend no lo envía, tendremos que inferirlo o usar una lógica diferente.
            # Por ahora, un placeholder si no viene:
            tipo_entrada = "General" # Considera cómo asignar esto correctamente
            logger.warning(f"Tipo de entrada no especificado para comprador {comprador_data.get('dni')}, usando '{tipo_entrada}'")
        
        precio_entrada = precios_entradas.get(tipo_entrada, 0) # Obtener precio de las solicitadas
        
        entrada_data = {
            'nombre': comprador_data.get('nombre'),
            'apellido': comprador_data.get('apellido'),
            'dni': comprador_data.get('dni'),
            'email': comprador_data.get('email'),
            'telefono': comprador_data.get('telefono'),
            'tipo_entrada': tipo_entrada, # Asegúrate de que este dato venga del formulario
            'precio_pagado': precio_entrada, # Usar el precio de la entrada individual
            'estado': 'activa',
            'created_at': datetime.now().isoformat(),
            'merchant_order_id': merchant_order_data.get('id'), # Referencia a la orden de MP
            'payment_ids': [p.get('id') for p in merchant_order_data.get('payments', []) if p.get('status') == 'approved']
        }

        ref = db.collection('eventos').document(evento_id).collection('entradas').document()
        entrada_data['id'] = ref.id

        qr = qrcode.make(ref.id)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        entrada_data['qr_code'] = qr_base64

        ref.set(entrada_data)
        logger.info(f"Entrada {ref.id} creada para DNI {entrada_data['dni']}.")

        # Enviar email
        try:
            _enviar_email_confirmacion(entrada_data, nombre_evento, evento_data) # Pasa evento_data para más info
            logger.info(f"Email de confirmación enviado a {entrada_data['email']}.")
        except Exception as e:
            logger.error(f"Error al enviar email a {entrada_data['email']}: {e}", exc_info=True)
            # No se relanza la excepción para no detener la creación de otras entradas.
            # Considera un sistema de reintentos para emails fallidos.

    logger.info("Proceso de creación de entradas y envío de emails completado.")

def _enviar_email_confirmacion(entrada_data, nombre_evento, evento_data):
    """
    Envía el email de confirmación con el QR.
    """
    msg = EmailMessage()
    msg['Subject'] = f'¡Tu entrada para {nombre_evento} ha sido confirmada!'
    msg['From'] = MAIL_FROM
    msg['To'] = entrada_data['email']

    # Contenido HTML del correo
    html_content = f"""
    <html>
    <body>
        <h2>¡Gracias por tu compra, {entrada_data['nombre']} {entrada_data['apellido']}!</h2>
        <p>Tu entrada para el evento <strong>{nombre_evento}</strong> ha sido confirmada.</p>
        <p><strong>Detalles de la entrada:</strong></p>
        <ul>
            <li><strong>Tipo de Entrada:</strong> {entrada_data['tipo_entrada']}</li>
            <li><strong>Precio Pagado:</strong> ${entrada_data['precio_pagado']} ARS</li>
            <li><strong>Evento:</strong> {nombre_evento}</li>
            <li><strong>Fecha:</strong> {evento_data.get('fecha', 'N/A')}</li>
            <li><strong>Lugar:</strong> {evento_data.get('lugar', 'N/A')}</li>
        </ul>
        <p>Aquí tienes tu código QR. Preséntalo en la entrada del evento:</p>
        <img src="data:image/png;base64,{entrada_data['qr_code']}" alt="Código QR de tu entrada">
        <p><strong>ID de Entrada:</strong> {entrada_data['id']}</p>
        <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
        <p>Atentamente,<br>El equipo de {nombre_evento}</p>
    </body>
    </html>
    """
    msg.set_content(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MAIL_USER, MAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        logger.error(f"Error al enviar email: {e}", exc_info=True)
        raise # Relanzar para que el llamador sepa que hubo un error