""" Un archivo que contiene utilidades para los archivos de la carpeta de Cuotas
(existe mas que nada para evitar un error de dependencia circular) """
from collections import OrderedDict
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from zoneinfo import ZoneInfo


def ordenar_datos_cuotas(data_cuota, precio_cuota, cuota_id):   
    """Ordena los datos de las cuotas en un formato especifico.

    Args:
        data_cuota (Dict): Diccionario de datos.
        precio_cuota (Number): Precio de la cuota.
        cuota_id (String): ID de la cuota a ordenar.

    Returns:
        OrderedDict: Datos de la cuota ordenados en formato de Diccionario.
    """
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


def get_monto_cuota(cuota_id, recargo_day):
    """Obtiene el precio de una cuota especifica, usando un dia de recargo especifico.

    Args:
        cuota_id (String): ID de la cuota.
        recargo_day (Integer): Numero entero del dia de recargo.

    Returns:
        HTTPError/Number: Retorna el monto de la cuota o lanza un error si algo va mal.
    """
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
    
    #TODO: Retorno de monto de alumno ingresado el 15 o despues
    
    #Retorno de montoBase
    return precios.get("montoBase")