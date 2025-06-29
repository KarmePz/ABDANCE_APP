import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import firestore
import mercadopago
from firebase_init import db
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from email.message import EmailMessage
import smtplib

# Cargar variables de entorno
load_dotenv()

def entradas(request, uid=None, role=None):
    if request.method == 'GET':
        return getEntradas(request)
    elif request.method == 'POST':
        return postEntrada(request)
    elif request.method == 'PUT':
        return putEntrada(request)

    elif request.method == 'DELETE':
        return {"Este metodo no esta disponible"}  # deleteEntrada(request)

    else:
        return {'error': 'Método no permitido'}, 405


# GET
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


# POST simple
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

    ref = db.collection('eventos').document(evento_id).collection('entradas').document()
    entrada_data['id'] = ref.id

    qr = qrcode.make(ref.id)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    entrada_data['qr_code'] = qr_base64

    ref.set(entrada_data)

    return {'mensaje': 'Entrada creada correctamente', 'entrada': entrada_data}, 201


# PUT para cambiar estado
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


def procesar_webhook(request):
    try:
        data = request.get_json()
        payment_id = data.get('data', {}).get('id')
        
        if not payment_id:
            return {'error': 'No se recibió payment_id'}, 400

        sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
        payment = sdk.payment().get(payment_id)["response"]
        
        if payment.get("status") != "approved":
            return {'mensaje': 'Pago no aprobado, no se crean entradas'}, 200

        external_ref = payment.get("external_reference", "")
        if "___" not in external_ref:
            return {'error': 'Formato de external_reference inválido'}, 400
            
        evento_id, form_id = external_ref.split("___")[:2]
        
        form_ref = db.collection("formularios_pendientes_pago").document(form_id)
        form_data = form_ref.get().to_dict()
        
        if not form_data:
            return {'error': 'Datos del formulario no encontrados'}, 404

        # Obtener datos del evento
        evento_ref = db.collection("eventos").document(evento_id)
        evento_data = evento_ref.get().to_dict()

        entradas_creadas = []
        for datos_comprador in form_data.get("datos_compradores", []):
            precio = None
            for entrada in form_data.get("entradas_solicitadas", []):
                if entrada.get("tipo") == datos_comprador.get("tipo_entrada"):
                    precio = entrada.get("precio")
                    break
            
            if not precio:
                continue

            entrada_data = {
                "nombre": datos_comprador.get("nombre", ""),
                "apellido": datos_comprador.get("apellido", ""),
                "dni": datos_comprador.get("dni", ""),
                "email": datos_comprador.get("email", ""),
                "telefono": datos_comprador.get("telefono", ""),
                "tipo_entrada": datos_comprador.get("tipo_entrada", ""),
                "evento_id": evento_id,
                "payment_id": payment_id,
                "precio": float(precio),
                "estado": "activa",
                "created_at": datetime.now().isoformat()
            }

            entrada_ref = db.collection("eventos").document(evento_id).collection("entradas").document()
            entrada_data["id"] = entrada_ref.id
            
            qr = qrcode.make(f"{entrada_ref.id}")
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            entrada_data["qr_code"] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            entrada_ref.set(entrada_data)
            entradas_creadas.append(entrada_data)
            
            # ENVIAR EMAIL DE CONFIRMACIÓN
            enviar_email_confirmacion_entrada(entrada_data, evento_data)

        form_ref.delete()

        return {'mensaje': f'Entradas creadas: {len(entradas_creadas)}', 'entradas': entradas_creadas}, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}, 500
    
# def enviar_email_confirmacion_entrada(entrada_data, evento_data):
#     """
#     Envía un email de confirmación con los datos de la entrada y el evento.
    
#     Args:
#         entrada_data (dict): Datos de la entrada (nombre, email, tipo_entrada, qr_code, etc.)
#         evento_data (dict): Datos del evento (nombre, fecha, lugar, etc.)
#     """
#     try:
#         # Configuración del servidor SMTP
#         smtp_server = "smtp.gmail.com"
#         smtp_port = 587
#         email_user = os.getenv("MAIL_USER")
#         email_pass = os.getenv("MAIL_PASS")
#         email_from = os.getenv("MAIL_FROM")

#         # Crear el mensaje de email
#         msg = EmailMessage()
#         msg['From'] = email_from
#         msg['To'] = entrada_data['email']
#         msg['Subject'] = f"✅ Confirmación de entrada - {evento_data['nombre']}"

#         # Cuerpo del email en HTML (diseño moderno)
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; }}
#                 .header {{ background-color: #6a1b9a; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
#                 .content {{ padding: 20px; }}
#                 .qr-code {{ text-align: center; margin: 20px 0; }}
#                 .details {{ background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 15px 0; }}
#                 .footer {{ text-align: center; font-size: 12px; color: #777; margin-top: 20px; }}
#                 .button {{ background-color: #6a1b9a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>¡Tu entrada ha sido confirmada!</h1>
#                 </div>
                
#                 <div class="content">
#                     <p>Hola {entrada_data['nombre']} {entrada_data['apellido']},</p>
#                     <p>Gracias por tu compra. Aquí tienes los detalles de tu entrada:</p>
                    
#                     <div class="details">
#                         <h2>📌 Detalles del Evento</h2>
#                         <p><strong>Evento:</strong> {evento_data['nombre']}</p>
#                         <p><strong>Fecha:</strong> {evento_data['fecha']}</p>
#                         <p><strong>Lugar:</strong> {evento_data['lugar']}</p>
#                         <p><strong>Tipo de entrada:</strong> {entrada_data['tipo_entrada']}</p>
#                         <p><strong>Precio:</strong> ${entrada_data['precio']:.2f}</p>
#                     </div>
                    
#                     <div class="qr-code">
#                         <h3>Tu código QR de acceso</h3>
#                         <img src="data:image/png;base64,{entrada_data['qr_code']}" alt="Código QR" width="200">
#                         <p><small>Presenta este código en la entrada del evento</small></p>
#                     </div>
                    
#                     <p>Guarda este email como comprobante de tu compra.</p>
                    
#                     <div class="footer">
#                         <p>Si tienes alguna pregunta, contáctanos respondiendo a este email.</p>
#                         <p>© {datetime.now().year} AbdanceApp - Todos los derechos reservados</p>
#                     </div>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """

#         msg.set_content(f"""
#         Confirmación de entrada - {evento_data['nombre']}
        
#         Hola {entrada_data['nombre']} {entrada_data['apellido']},
        
#         Gracias por tu compra. Aquí tienes los detalles de tu entrada:
        
#         Evento: {evento_data['nombre']}
#         Fecha: {evento_data['fecha']}
#         Lugar: {evento_data['lugar']}
#         Tipo de entrada: {entrada_data['tipo_entrada']}
#         Precio: ${entrada_data['precio']:.2f}
        
#         Presenta el código QR adjunto en la entrada del evento.
        
#         © {datetime.now().year} AbdanceApp
#         """)
        
#         msg.add_alternative(html_content, subtype='html')

#         # Adjuntar el QR como imagen
#         qr_img = base64.b64decode(entrada_data['qr_code'])
#         msg.add_attachment(qr_img, maintype='image', subtype='png', filename='codigo-qr.png')

#         # Enviar el email
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(email_user, email_pass)
#             server.send_message(msg)
            
#         print(f"📧 Email enviado a {entrada_data['email']}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Error al enviar email: {str(e)}")
#         return False

import os
import base64
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime

def enviar_email_confirmacion_entrada(entrada_data, evento_data):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_user = os.getenv("MAIL_USER")
        email_pass = os.getenv("MAIL_PASS")
        email_from = os.getenv("MAIL_FROM")

        msg = EmailMessage()
        msg['From'] = email_from
        msg['To'] = entrada_data['email']
        msg['Subject'] = f"✅ Confirmación de entrada - {evento_data['nombre']}"

        msg.set_content(f"""
        Hola {entrada_data['nombre']} {entrada_data['apellido']},

        Gracias por tu compra. Aquí tienes los detalles de tu entrada:

        Evento: {evento_data['nombre']}
        Fecha: {evento_data['fecha']}
        Lugar: {evento_data['lugar']}
        Tipo de entrada: {entrada_data['tipo_entrada']}
        Precio: ${entrada_data['precio']:.2f}

        Presenta el código QR en la entrada del evento.
        """)

        # 🧩 Generar un CID único para la imagen QR
        qr_cid = make_msgid(domain="abdanceapp.local")[1:-1]  # Quita los < >

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; }}
                .header {{ background: #6a1b9a; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .details {{ background: #f4f4f4; padding: 15px; border-radius: 8px; margin-top: 15px; }}
                .qr-code {{ text-align: center; margin: 20px 0; }}
                .footer {{ font-size: 12px; color: #888; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Tu entrada ha sido confirmada!</h1>
                </div>
                <p>Hola {entrada_data['nombre']} {entrada_data['apellido']},</p>
                <p>Gracias por tu compra. Aquí tienes los detalles:</p>

                <div class="details">
                    <p><strong>Evento:</strong> {evento_data['nombre']}</p>
                    <p><strong>Fecha:</strong> {evento_data['fecha']}</p>
                    <p><strong>Lugar:</strong> {evento_data['lugar']}</p>
                    <p><strong>Tipo de entrada:</strong> {entrada_data['tipo_entrada']}</p>
                    <p><strong>Precio:</strong> ${entrada_data['precio']:.2f}</p>
                </div>

                <div class="qr-code">
                    <h3>🎟️ Tu código QR</h3>
                    <img src="cid:{qr_cid}" width="200" alt="Código QR">
                    <p><small>Presenta este código en la entrada del evento</small></p>
                </div>

                <p class="footer">
                    Si tienes alguna duda, responde a este email.<br>
                    © {datetime.now().year} AbdanceApp - Todos los derechos reservados
                </p>
            </div>
        </body>
        </html>
        """

        msg.add_alternative(html_content, subtype='html')

        # 📷 Adjuntar imagen QR como recurso embebido con cid
        qr_img_bytes = base64.b64decode(entrada_data['qr_code'])
        msg.get_payload()[1].add_related(qr_img_bytes, 'image', 'png', cid=qr_cid)

        # Enviar correo
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)

        print(f"✅ Email enviado a {entrada_data['email']}")
        return True

    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False
