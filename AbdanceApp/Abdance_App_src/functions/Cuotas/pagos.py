import mercadopago
import os
from datetime import datetime
from firebase_init import db  # Firebase con base de datos inicializada
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv
from functions.Cuotas.utilidades_cuotas import get_monto_cuota, ordenar_datos_cuotas
from dateutil import parser
from zoneinfo import ZoneInfo


@require_auth(required_roles=['alumno', 'admin'])
def crear_preferencia_cuota(request, uid=None, role=None):
    try:
        #Primero obtiene la cuota a pagar
        data = request.get_json(silent=True) or {}
        cuota_id = data.get('cuota_id')
        dia_recargo = data.get('dia_recargo')

        #Verifica que no falten datos importantes.
        if not data or 'cuota_id' not in data or 'dia_recargo' not in data:
            return {'error': 'El dia de recargo (dia_recargo) y el id de la cuota (cuota_id) son requeridos obligatoriamente.'}, 400  
            
        cuota_ref = db.collection('cuotas').document(cuota_id)
        cuota_doc = cuota_ref.get()
        cuota_data = None

        if cuota_doc.exists: 
            cuota_data = cuota_doc.to_dict()
            precio_cuota = get_monto_cuota(cuota_id, dia_recargo)

            cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota, cuota_doc.id)
        else:
            return {'error': "Cuota no encontrada."}, 404
        
        disciplina_doc = db.collection("disciplinas").document(cuota_data["idDisciplina"]).get()
        if not disciplina_doc.exists:
            return {'error': "Esta cuota no pertenece a ninguna disciplina."}, 500
        
        disciplina_data = disciplina_doc.to_dict()

        #Luego, si todo fue bien, obtiene los datos del .env
        load_dotenv()
        PROD_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN_TEST")

        mercado_pago_sdk = mercadopago.SDK(str(PROD_ACCESS_TOKEN))

        #Creacion de la preferencia
        preference_data = {
            "items": [
                {
                    "title": f"Cuota {cuota_data["concepto"]}",
                    "quantity": 1,
                    "unit_price": int(cuota_data["precio_cuota"]),
                    "currency_id": "ARS",
                    "description": f"Cuota del mes de {cuota_data["concepto"]}, para alumno con DNI: {cuota_data["dniAlumno"]}, de la disciplina: {disciplina_data["nombre"]}.",
                }
            ],
            "back_urls": {
                "success": "https://www.nationstates.net/nation=midnight_horrors",
                "failure": "https://www.youtube.com",
                "pending": "https://www.google.com",
            },
            "auto_return": "approved",
            "payment_methods": {
                "excluded_payment_methods": [
                {
                    "id": ""
                }
                ],
                "excluded_payment_types": [
                {
                    "id": "ticket"
                }
                ]
            },
            "external_reference": f"{cuota_data["id"]}",
            "metadata": {
                "tipo_objeto_a_pagar": "cuota"
            }
        }
        preference_response = mercado_pago_sdk.preference().create(preference_data)
        preference = preference_response["response"]

        return preference, 200 
    
    except Exception as e:
        return {'error': str(e)}, 500


def establecer_pago(data_payment):
    PROD_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN_TEST")
    mercado_pago_sdk = mercadopago.SDK(str(PROD_ACCESS_TOKEN))

    #Obtiene información del pago
    informacion_pago = mercado_pago_sdk.payment().get(data_payment)
    pago = informacion_pago["response"]
    id_objeto = pago.get("external_reference")
    tipo_objeto = pago.get("metadata", {}).get("tipo_objeto_a_pagar").lower()
    status_pago = pago.get("status")
    cantidad_transaccion = pago.get("transaction_amount")

    if status_pago == "approved" and id_objeto and tipo_objeto == "cuota":
        cuota_ref = db.collection('cuotas').document(id_objeto)

        if cuota_ref.get().to_dict().get("estado", "").lower() == "pagada":
            raise LookupError("La cuota buscada ya está pagada.")
        
        raw_date = pago.get("date_approved")
        dt = datetime.fromisoformat(raw_date)                  # crea datetime con tzinfo
        dt_local = dt.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
        
        cuota_ref.update({
            'estado': 'pagada',
            'fechaPago': dt_local,
            'metodoPago': pago.get('payment_type_id'),
            'montoPagado': cantidad_transaccion
        })
    #TODO:Logica para el pago de las entradas de eventos aquí    
    elif status_pago == "approved" and id_objeto and tipo_objeto == "entrada_evento":
        return 
    
    