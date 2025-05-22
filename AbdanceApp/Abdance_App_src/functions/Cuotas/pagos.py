import mercadopago
import os
from firebase_init import db  # Firebase con base de datos inicializada
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv
from cuotas import get_monto_cuota, ordenar_datos_cuotas



def efectuar_pago(request):
    try:
        #Primero obtiene la cuota a pagar
        data = request.get_json(silent=True) or {}
        cuota_id = data.get('cuota_id')
        dia_recargo = data.get('dia_recargo')

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
            "external_reference": f"{cuota_data["id"]}"
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
    id_cuota = pago.get("external_reference")
    status_pago = pago.get("status")

    if status_pago == "approved" and id_cuota:
        cuota_ref = db.collection('cuotas').document(id_cuota)
        cuota_ref.update({
            'estado': 'pagada',
            'fechaPago': pago.get('date_approved')
        })