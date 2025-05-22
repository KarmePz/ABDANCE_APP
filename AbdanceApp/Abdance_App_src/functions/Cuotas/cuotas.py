import json
import functions_framework
import firebase_admin
import mercadopago
import os
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
import hashlib
import hmac
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from pagos import establecer_pago



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
        #axiox no permite GETs con datos en JSON, por lo que es necesario usar los args.
        data = request.args
        cuota_id = data.get('cuota_id')

        #ID de la disciplina asi se pide cuotas especificas de una disciplina
        id_disciplina = data.get('idDisciplina') 
        #DNI del alumno para pedir las cuotas de este solamente
        dni_alumno = data.get('dniAlumno')
        
        #El dia de recargo, asi solo se debe pasar por el front
        #EL DIA DE RECARGO ES REQUERIDO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if 'dia_recargo' not in data:
            return {'error': 'El dia de recargo (dia_recargo) es requerido obligatoriamente para evitar errores.'}, 400
        
        recargo_day = int(data.get('dia_recargo'))

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
                cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota, doc.id)

                cuotas.append(cuota_data)

            return cuotas, 200

        cuota_ref = db.collection('cuotas').document(cuota_id)
        cuota_doc = cuota_ref.get()

        if cuota_doc.exists: 
            cuota_data = cuota_doc.to_dict()
            precio_cuota = get_monto_cuota(cuota_id, recargo_day)

            cuota_data = ordenar_datos_cuotas(cuota_data, precio_cuota, cuota_doc.id)

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

    return determinar_monto(concepto_cuota, precios, estado_cuota, fecha_pago_cuota, int(recargo_day))


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


def ordenar_datos_cuotas(data_cuota, precio_cuota, cuota_id):   
    #Se arma el diccionario con orden especifico
    cuota_data = OrderedDict()
    cuota_data["id"] = cuota_id
    cuota_data["concepto"] = data_cuota.get("concepto")
    cuota_data["dniAlumno"] = data_cuota.get("dniAlumno")
    cuota_data["estado"] = data_cuota.get("estado")
    cuota_data["fechaPago"] = data_cuota.get("fechaPago")
    cuota_data["idDisciplina"] = data_cuota.get("idDisciplina")
    cuota_data["metodoPago"] = data_cuota.get("metodoPago")
    cuota_data["precio_cuota"] = precio_cuota
        
    return cuota_data


def pagar_cuota(request):
    try:
        #Obtiene el ID de la request y la firma de la notificación.
        request_id = request.headers.get("X-Request-Id")
        signature = request.headers.get("X-Signature")

        #Obtiene los datos del body y la query de la notificacion.
        data = request.get_json(silent=True) or {}
        parametros_query = request.args
        data_id = parametros_query.get("data.id")

        #Parte la firma en sus dos partes correspondientes y crea las variables donde se pondrán.
        partes_signature = signature.split(",")
        timestamp = None
        hash_v1 = None

        #Itera sobre cada una para asignar sus valores a cada parte.
        for parte in partes_signature:
            key_value = parte.split("=", 1)
            if len(key_value) == 2:
                key = key_value[0].strip() 
                value = key_value[1].strip() 

                if key == "ts":
                    timestamp = value
                elif key == "v1":
                    hash_v1 = value

        load_dotenv()
        WEBHOOK_KEY = os.getenv("MP_WEBHOOK_KEY")
        
        #Creación del manifiesto y codificación de la firma
        manifiesto = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
        firma_hmac = hmac.new(WEBHOOK_KEY.encode(), msg=manifiesto.encode(), digestmod=hashlib.sha256)
        resultado_sha = firma_hmac.hexdigest()

        if resultado_sha == hash_v1:
            topic = parametros_query.get("type")

            if topic == "payment":
                establecer_pago(data["data"]["id"])

            return "success", 200
        else:
            return "failure", 400
    
    except Exception as e:
        return {'error': str(e)}, 500