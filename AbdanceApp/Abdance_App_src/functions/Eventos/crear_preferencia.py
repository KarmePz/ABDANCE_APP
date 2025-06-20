import os
from dotenv import load_dotenv
import mercadopago
from flask import jsonify
from firebase_init import db
from datetime import datetime
import uuid

# Cargar variables de entorno
load_dotenv()

# Leer el token de Mercado Pago
ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("Falta MERCADOPAGO_ACCESS_TOKEN en el archivo .env")

# Inicializar el SDK de Mercado Pago
sdk = mercadopago.SDK(ACCESS_TOKEN)

def crear_preferencia(request):
    try:
        data = request.get_json()

        evento_id = data.get("evento_id")
        entradas = data.get("entradas")
        form_id = data.get("form_id")  # ✅ Ahora lo tomás del frontend
        nombre_evento = data.get("nombreEvento")
        lugar = data.get("lugar")
        fecha = data.get("fecha")
        imagen = data.get("imagen")

        if not evento_id or not entradas or not form_id:
            return jsonify({"error": "Faltan datos requeridos"}), 400

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
        for entrada in entradas:
            tipo = entrada.get("tipo")
            cantidad = entrada.get("cantidad")

            if not tipo or not cantidad:
                return jsonify({"error": "Faltan campos en una entrada"}), 400

            precio = precios.get(tipo)
            if precio is None:
                return jsonify({"error": f"Tipo de entrada '{tipo}' no válido"}), 400

            items.append({
                "title": f"Entrada {tipo} - Evento {nombre_evento}",
                "quantity": int(cantidad),
                "unit_price": float(precio),
                "currency_id": "ARS"
            })

        # 📤 Crear preferencia de pago
        preference_data = {
            "items": items,
            "external_reference": f"{evento_id}__{form_id}",
            "back_urls": {
                "success": f"https://45b8-190-183-84-54.ngrok-free.app/pago-exitoso?eventoId={evento_id}&formId={form_id}",
                "failure": "https://tusitio.com/pago-error",
                "pending": "https://tusitio.com/pago-pendiente"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)

        if "response" not in preference_response:
            return jsonify({
                "error": "Respuesta inválida de MercadoPago",
                "detalle": preference_response
            }), 500

        init_point = preference_response["response"].get("init_point")
        if not init_point:
            return jsonify({
                "error": "No se pudo generar el init_point",
                "detalle": preference_response["response"]
            }), 500

        print("✅ init_point generado:", init_point)

        return jsonify({
            "init_point": init_point,
            "formId": form_id
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
