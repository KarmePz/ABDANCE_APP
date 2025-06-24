import os
from dotenv import load_dotenv
import mercadopago
from flask import jsonify
from firebase_init import db
from datetime import datetime
import uuid
import json # ✅ Importar json
import firebase_admin # ✅ Asegurarse de que firebase_admin esté importado
from firebase_admin import firestore # ✅ AGREGAR ESTA IMPORTACIÓN

# Cargar variables de entorno
load_dotenv()

# Leer el token de Mercado Pago
ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("Falta el token MERCADOPAGO_ACCESS_TOKEN.")

# Inicializar el SDK de Mercado Pago
sdk = mercadopago.SDK(ACCESS_TOKEN)

def crear_preferencia(request):
    try:
        data = request.get_json()
        
        evento_id = data.get("evento_id")
        entradas_solicitadas = data.get("entradas") # Renombrado para claridad
        form_id = str(uuid.uuid4())  # ✅ Generar un form_id único aquí
        nombre_evento = data.get("nombreEvento")
        lugar = data.get("lugar")
        fecha = data.get("fecha")
        imagen = data.get("imagen")
        # ✅ Capturar los datos de los formularios de los compradores
        datos_compradores = data.get("datosCompradores") 

        if not evento_id or not entradas_solicitadas or not datos_compradores: # ✅ Validar datos_compradores
            return jsonify({"error": "Faltan datos requeridos para crear la preferencia."}), 400

        # 🔒 Obtener datos del evento desde Firestore
        evento_ref = db.collection("eventos").document(evento_id)
        evento_doc = evento_ref.get()

        if not evento_doc.exists:
            return jsonify({"error": "Evento no encontrado"}), 404

        evento_data = evento_doc.to_dict()
        entradas_disponibles = evento_data.get("entradas", [])

        # 🔍 Lookup de precios por tipo
        precios = {entrada["tipo"]: entrada["precio"] for entrada in entradas_disponibles}

        # 🔄 Armar ítems con precios
        items = []
        for entrada in entradas_solicitadas: # Usar entradas_solicitadas
            tipo = entrada.get("tipo")
            cantidad = entrada.get("cantidad")

            if not tipo or not cantidad:
                return jsonify({"error": "Faltan campos en una entrada solicitada."}), 400

            precio = precios.get(tipo)
            if precio is None:
                return jsonify({"error": f"Tipo de entrada '{tipo}' no válido."}), 400

            items.append({
                "title": f"Entrada {tipo} - Evento {nombre_evento}",
                "quantity": int(cantidad),
                "unit_price": float(precio),
                "currency_id": "ARS"
            })
        
        
        form_temporal_ref = db.collection("formularios_pendientes_pago").document(form_id)
        form_temporal_ref.set({
            "evento_id": evento_id,
            "entradas_solicitadas": entradas_solicitadas, # Guardamos también las entradas solicitadas con su tipo y cantidad
            "datos_compradores": datos_compradores,
            "created_at": firestore.SERVER_TIMESTAMP # Para posible limpieza de registros antiguos
        })
        print(f"✅ Datos del formulario temporal guardados con ID: {form_id}")

        NOTIFICATION_URL_DEBUG = os.getenv("MP_NOTIFICATION_URL")
        print(f"DEBUG: MP_NOTIFICATION_URL leída: {NOTIFICATION_URL_DEBUG}")
        # 📤 Crear preferencia de pago
        preference_data = {
            "items": items,
            "external_reference": f"{evento_id}___{form_id}", # Usamos form_id aquí
            "back_urls": {
                "success": f"https://abdance-app-frontend-c468f05iv-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=approved&external_reference={evento_id}___{form_id}",
                "failure": f"https://abdance-app-frontend-c468f05iv-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=failure&external_reference={evento_id}___{form_id}",
                "pending": f"https://abdance-app-frontend-c468f05iv-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=pending&external_reference={evento_id}___{form_id}"
            },
            "auto_return": "approved",
            "notification_url": NOTIFICATION_URL_DEBUG # ✅ Usar variable de entorno
        }

        # Asegúrate de que tu `MP_NOTIFICATION_URL` apunte a `/webhook/mercadopago` de tu Cloud Function
        # Ejemplo: https://REGION-PROJECT_ID.cloudfunctions.net/main/webhook/mercadopago

        preference_response = sdk.preference().create(preference_data)

        if "response" not in preference_response:
            # Si hay un error al crear la preferencia, eliminar el registro temporal
            form_temporal_ref.delete()
            return jsonify({
                "error": "Respuesta inválida de MercadoPago al crear preferencia",
                "detalle": preference_response
            }), 500

        init_point = preference_response["response"].get("init_point")
        if not init_point:
            # Si hay un error al crear la preferencia, eliminar el registro temporal
            form_temporal_ref.delete()
            return jsonify({
                "error": "No se pudo generar el init_point en MercadoPago",
                "detalle": preference_response["response"]
            }), 500

        print("✅ init_point generado:", init_point)

        return jsonify({
            "init_point": init_point,
            "formId": form_id # Devolvemos el form_id para que el frontend lo pueda usar en las back_urls
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500