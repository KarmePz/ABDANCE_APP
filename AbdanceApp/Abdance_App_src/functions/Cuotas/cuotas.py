import json
import functions_framework
import firebase_admin
import mercadopago
import os
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
import mercadopago.config
import mercadopago.config.request_options
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime, time
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv
from zoneinfo import ZoneInfo


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

            cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota)
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
        }

        preference_response = mercado_pago_sdk.preference().create(preference_data)
        preference = preference_response["response"]

        return preference, 200 
    
    except Exception as e:
        return {'error': str(e)}, 500


def cuotas(request):
    if request.method == "GET":
        return getCuotas(request)
    
    elif request.method == 'POST':
        return postCuotas(request)
        
    
    elif request.method == 'PUT':
        return putCuotas(request)
    
    elif request.method == 'DELETE':
        return deleteCuotas(request)
    
    else:
        return 'hola pagos', 200


#@require_auth(required_roles=['alumno', 'profesor', 'admin'])
def getCuotas(request):
    try:
        data = request.args
        cuota_id = data.get('cuota_id')

        #ID de la disciplina asi se pide cuotas especificas de una disciplina
        id_disciplina = data.get('idDisciplina') 
        #DNI del alumno para pedir las cuotas de este solamente
        dni_alumno = data.get('dniAlumno')
        
        #El dia de recargo, asi solo se debe pasar por el front
        #EL DIA DE RECARGO ES REQUERIDO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        recargo_day = int(data.get('dia_recargo'))
        if "dia_recargo" not in data:
            return {'error': 'El dia de recargo (dia_recargo) es requerido obligatoriamente para evitar errores.'}, 400

        if not data or 'cuota_id' not in data:
            cuotas = []
            cuotas_ref = db.collection('cuotas')

            #Filtros para traer por disciplina y/o alumno
            if id_disciplina is not None:
                cuotas_ref = cuotas_ref.where("idDisciplina", "==", id_disciplina)

            if dni_alumno is not None:
                cuotas_ref = cuotas_ref.where("dniAlumno", "==", dni_alumno)

            for doc in cuotas_ref.stream():
                cuota_data = doc.to_dict()
            
                precio_cuota = get_monto_cuota(doc.id, recargo_day)
                cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota)

                cuotas.append(cuota_data)

            return cuotas, 200

        cuota_ref = db.collection('cuotas').document(cuota_id)
        cuota_doc = cuota_ref.get()

        if cuota_doc.exists: 
            cuota_data = cuota_doc.to_dict()
            precio_cuota = get_monto_cuota(cuota_id, recargo_day)

            cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota)

            return cuota_data, 200
        else:
            return {'error':'cuota no encontrada'}, 404
        
    except Exception as e:
        return {'error': str(e)}, 500


def get_monto_cuota(cuota_id, recargo_day):
    cuota_ref = db.collection('cuotas').document(cuota_id)
    cuota_doc = cuota_ref.get()
    if not cuota_doc.exists:
        return {'error':'Una de las cuotas no fue encontrada.'}, 404
    
    cuota_data = cuota_doc.to_dict()
    disciplina_id = cuota_data.get("idDisciplina")
    if not disciplina_id:
        return {'error':'Una de las cuotas no tiene disciplina asignada.'}, 400
    
    disciplina_ref = db.collection("disciplinas").document(disciplina_id)
    disciplina_doc = disciplina_ref.get()
    if not disciplina_doc.exists:
        return {'error':'Una de las disciplinas no fue encontrada o no existe.'}, 400
    
    precios = disciplina_doc.to_dict().get("precios", {})
    concepto_cuota = cuota_data.get("concepto")
    estado_cuota = cuota_data.get("estado", "").lower()
    fecha_pago_cuota = cuota_data.get("fechaPago")

    return determinar_monto(concepto_cuota, precios, estado_cuota, fecha_pago_cuota, recargo_day)


def determinar_monto(concepto_cuota, precios, estado, fecha_pago, recargo_day):
    #Retorno de matricula
    if concepto_cuota == "matricula":
        return precios.get("matriculaAnual")
    
    #Calculo y Retorno de montoRecargo
    today = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

    def en_recargo(dt: datetime):
        # dt aquí ya será tz-aware si viene de Firestore, o naive si no,
        # así que iguala ambos usando .astimezone(...) o ignorando tzinfo
        local = dt
        if dt.tzinfo:
            local = dt.astimezone(ZoneInfo("America/Argentina/Buenos_Aires"))
        return local.day >= recargo_day

    pago_dt = None
    if fecha_pago:
        if isinstance(fecha_pago, str):
            pago_dt = datetime.fromisoformat(fecha_pago)
        else:
            pago_dt = fecha_pago

    if (estado != "pagada" and en_recargo(today)) or (pago_dt and en_recargo(pago_dt)):
        return precios.get("montoRecargo")
    
    #Retorno de montoBase
    return precios.get("montoBase")


def ordenar_datos_cuotas(data_cuota, precio_cuota):   # Armamos el diccionario con orden especifico para hacerlo mas legible
    cuota_data = OrderedDict()
    cuota_data["concepto"] = data_cuota.get("concepto")
    cuota_data["dniAlumno"] = data_cuota.get("dniAlumno")
    cuota_data["estado"] = data_cuota.get("estado")
    cuota_data["fechaPago"] = data_cuota.get("fechaPago")
    cuota_data["idDisciplina"] = data_cuota.get("idDisciplina")
    cuota_data["metodoPago"] = data_cuota.get("metodoPago")
    cuota_data["precio_cuota"] = precio_cuota
        
    return cuota_data
