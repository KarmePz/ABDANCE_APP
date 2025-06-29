import os
from dotenv import load_dotenv
import mercadopago
from flask import jsonify
from util.cors import apply_cors_manual

from firebase_init import db
from datetime import datetime
import uuid
import json 


from firebase_admin import firestore 

load_dotenv()


ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("Falta el token MERCADOPAGO_ACCESS_TOKEN.")


sdk = mercadopago.SDK(ACCESS_TOKEN)

def crear_preferencia(request):
    try:
        data = request.get_json()
        
        evento_id = data.get("evento_id")
        entradas_solicitadas = data.get("entradas") 
        form_id = str(uuid.uuid4())  
        nombre_evento = data.get("nombreEvento")
        lugar = data.get("lugar")
        fecha = data.get("fecha")
        imagen = data.get("imagen")
       
        datos_compradores = data.get("datosCompradores") 

        if not evento_id or not entradas_solicitadas or not datos_compradores: 
            return jsonify({"error": "Faltan datos requeridos para crear la preferencia."}), 400

        
        evento_ref = db.collection("eventos").document(evento_id)
        evento_doc = evento_ref.get()

        if not evento_doc.exists:
            return jsonify({"error": "Evento no encontrado"}), 404

        evento_data = evento_doc.to_dict()
        entradas_disponibles = evento_data.get("entradas", [])

        
        precios = {entrada["tipo"]: entrada["precio"] for entrada in entradas_disponibles}

        
        items = []
        for entrada in entradas_solicitadas: 
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
            "entradas_solicitadas": entradas_solicitadas, 
            "datos_compradores": datos_compradores,
            "created_at": firestore.SERVER_TIMESTAMP # Para posible limpieza de registros antiguos
        })
        print(f"✅ Datos del formulario temporal guardados con ID: {form_id}")

        
        # 📤 Crear preferencia de pago
        preference_data = {
            "items": items,
            "external_reference": f"{evento_id}___{form_id}", # Usamos form_id aquí
            "back_urls": {
                "success": f"https://abdance-app-frontend-c5qs95aip-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=approved&external_reference={evento_id}___{form_id}",
                "failure": f"https://abdance-app-frontend-c5qs95aip-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=failure&external_reference={evento_id}___{form_id}",
                "pending": f"https://abdance-app-frontend-c5qs95aip-camilos-projects-fd28538a.vercel.app/estado-pago?collection_status=pending&external_reference={evento_id}___{form_id}"
            },
            "auto_return": "approved",
            "notification_url": "https://southamerica-east1-snappy-striker-455715-q2.cloudfunctions.net/main/procesar_webhook"
        }

        
        preference_response = sdk.preference().create(preference_data)

        if "response" not in preference_response:
            
            form_temporal_ref.delete()
            return jsonify({
                "error": "Respuesta inválida de MercadoPago al crear preferencia",
                "detalle": preference_response
            }), 500

        init_point = preference_response["response"].get("init_point")
        if not init_point:
            
            form_temporal_ref.delete()
            return jsonify({
                "error": "No se pudo generar el init_point en MercadoPago",
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
        return {"error": str(e)}, 500