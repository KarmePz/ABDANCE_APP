import os
from firebase_admin import credentials, firestore, auth
import hashlib
import hmac
from firebase_init import db  # Firebase con base de datos inicializada
from functions.Usuarios.auth_decorator import require_auth
from dotenv import load_dotenv
from functions.Cuotas.pagos import establecer_pago
from functions.Cuotas.utilidades_cuotas import get_monto_cuota, ordenar_datos_cuotas
from datetime import datetime
from zoneinfo import ZoneInfo



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


def postCuotas(request):
    try:
        data_cuota = request.get_json(silent=True) or {}
        #se debe crear una nueva disciplina
        cuota_concepto = data_cuota.get("concepto")
        cuota_alumno = data_cuota.get("dniAlumno")
        cuota_disciplina = data_cuota.get("idDisciplina")
        
        if not cuota_concepto or not cuota_alumno or not cuota_disciplina:
            return {'error': 'Faltan datos para generar la cuota. Revise concepto, DNI del alumno, ID de disciplina.'}, 400

        #si todos los datos existen se añaden a la base de datos
        cuota_ref = db.collection("cuotas").document()
        
        #generar el id aleatorio
        cuota_id = cuota_ref.id
        data_cuota['id'] = cuota_id

        #Generar datos pre_establecidos
        data_cuota['estado'] = "pendiente"
        data_cuota['fechaPago'] = ""
        data_cuota['metodoPago'] = ""
        data_cuota['montoPagado'] = 0
        
        #guardar documento con el id
        cuota_ref.set(data_cuota)
        
        return {'message': 'Cuota registrada exitosamente'}, 201

    except Exception as e:
        return {'error': str(e)}, 500


def putCuotas(request):
    try:
        data = request.get_json(silent=True) or {} 
    
        if not data or 'cuota_id' not in data:
            return {'error': ' Ingrese un id (cuota_id) para poder actualizar la cuota.'}, 400
        
        #Verificacion de existencia de disciplina y alumno
        disciplina_id = data.get("idDisciplina")
        disciplina_ref = db.collection("disciplinas").document(disciplina_id)
        disciplina_doc = disciplina_ref.get()
        if not disciplina_doc.exists and disciplina_id:
            return {'error':'La disciplina proporcionada no fue encontrada o no existe.'}, 400
        
        alumno_dni = data.get("dniAlumno")
        alumno_ref = db.collection("usuarios").document(alumno_dni)
        alumno_doc = alumno_ref.get()
        if not alumno_doc.exists and alumno_dni:
            return {'error':'El alumno proporcionado no fue encontrado o no existe.'}, 400
        
        #Se realiza una comprobación de los campos, para no ingresar campos incorrectos
        #o que no corresponden.
        campos_permitidos = {
            'cuota_id',
            'concepto',       
            'estado',    
            'fechaPago',  
            'idDisciplina', 
            'dniAlumno',
            'metodoPago',
            'montoPagado',
        }

        campos_data = set(data.keys())
        campos_extra = campos_data - campos_permitidos
        if campos_extra:
            return {
                'error': 'Campos no permitidos en la petición.',
                'invalid_fields': list(campos_extra)
            }, 400
        
        cuota_ref = db.collection('cuotas').document(data['cuota_id'])
        cuota_doc = cuota_ref.get()
        cuota_data = cuota_doc.to_dict()
        
        #control de errores 
        if not cuota_doc.exists:
            return {'error': 'No se encontro la cuotaa especificada.'}, 404
        
        data.pop("cuota_id")
        cuota_ref.update(data)
        return {"message": "Cuota Actualizada", "id": cuota_data.get('id')}, 200

    except Exception as e:
        return {'error': str(e)}, 500


def deleteCuotas(request):
    try:
        data = request.get_json(silent=True) or {} 
    
        if not data or 'cuota_id' not in data:
            return {'error': 'Debe ingresar el id de la cuota (cuota_id) para poder eliminarla.'}, 400 
        
        cuota_ref = db.collection('cuotas').document(data['cuota_id'])
        cuota_doc = cuota_ref.get()
        
        #control de errores 
        if not cuota_doc.exists:
            return {'error': 'No se encontró la cuota especificada.'}, 404
        
        #eliminacion de BD firestore
        cuota_ref.delete()
        return {'message': 'Cuota eliminada correctamente.'}, 200

    except Exception as e:
        return {'error': str(e)}, 500


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

            return {"received": "true"}, 200
        else:
            return '', 200
    
    except Exception as e:
        return {'error': str(e)}, 500


def pagar_cuotas_manualmente(request_cuotas_id):
    try:
        data = request_cuotas_id.get_json(silent=True) or {}
        req_args = request_cuotas_id.args
        lista_cuotas_id = data.get("lista_cuotas", [])

        if not isinstance(lista_cuotas_id, list) or not lista_cuotas_id:
            return {'error': "El campo de \"lista_cuotas\" no es una lista o no está definido."}
        
        if 'dia_recargo' not in req_args:
            return {'error': 'El dia de recargo (dia_recargo) es requerido obligatoriamente para evitar errores.'}, 400
        recargo_day = req_args.get("dia_recargo")

        for id_cuota in lista_cuotas_id:
            cuota_ref = db.collection('cuotas').document(id_cuota)
            cuota_doc = cuota_ref.get()
            monto_pagado = get_monto_cuota(cuota_doc.id, recargo_day)

            #SE ASUME QUE EL PAGO SE HACE EN EFECTIVO
            if cuota_doc.exists: 
                cuota_ref.update({
                'estado': 'pagada',
                'fechaPago': datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")),
                'metodoPago': "cash",
                'montoPagado': monto_pagado
            })
            else:
                return {'error':'Una cuota no fue encontrada.'}, 404
        
        return "Cuotas pagadas manualmente con éxito.", 200


    except Exception as e:
        return {'error': str(e)}, 500


def crear_cuotas_mes(request):
    """Funcion que crea las cuotas para todos los alumnos de cada una de las disciplinas en las
    que estén agregados.

    Args:
        request (Data): Datos de la HTTP Request.

    Returns:
        HTTPResponse: Responde apropiadamente con error o un 201 dependiendo de si todo salió bien.
    """
    try:
        #TODO: Terminar estas dos funciones.
        usuario_ref = db.collection('usuarios').where('rol', '==', "alumno").stream()

        for doc_alumno in usuario_ref:
            doc_alumno.to_dict()

            

        return


    except Exception as e:
        return {'error': str(e)}, 500


def eliminar_cuotas_mes(request):
    try:
        return


    except Exception as e:
        return {'error': str(e)}, 500