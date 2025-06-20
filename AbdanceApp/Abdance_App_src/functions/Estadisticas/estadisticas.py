from typing import OrderedDict
from firebase_init import db
from datetime import datetime
from functions.Usuarios.auth_decorator import require_auth
from functions.Otros.utilidades_datetime import MESES_REVRSD
import pandas as pd



def fetch_pagadas():
    """Recupera todas las cuotas con estado "pagada" y devuelve una lista de dicts.

    Args:
        None

    Returns:
        Dict: Un diccionario con el formato: 
        - fechaPago: datetime
        - montoPagado: float
    """
    cuotas_pagadas = db.collection('cuotas').where('estado', '==', 'pagada').stream()
    dict_to_return = []

    for cuota in cuotas_pagadas:
        cuota_dict = cuota.to_dict()
        fecha_pago = cuota_dict.get('fechaPago')

        # Se normaliza a datetime
        if isinstance(fecha_pago, str):
            dt = datetime.fromisoformat(fecha_pago)
        else:
            dt = fecha_pago  # El Firestore Timestamp ya se normaliza a datetime

        monto = cuota_dict.get('montoPagado') or 0
        dict_to_return.append({'fechaPago': dt, 'montoPagado': monto, 'concepto': cuota.get('concepto'), 'DNIAlumno': cuota.get('dniAlumno')})

    return dict_to_return


@require_auth(required_roles=['admin'])
def total_pagado_mes(request, uid=None, role=None):
    try:
        data = request.get_json(silent=True) or {}

        if not data or ('year' and 'month') not in data:
            return {'error': "Se debe especificar un mes (month) y año (year)."}, 400
        
        anio_filtro = data.get('year')
        mes_filtro = data.get('month')

        if mes_filtro not in range(1, 12):
            return {'error': "Se debe especificar un numero de mes válido: 1-Enero, 2-Febrero, ... , 12-Diciembre"}, 400
        if anio_filtro > datetime.now().year or anio_filtro < 1:
            return {'error': "Se debe especificar un numero de año válido a partir del año actual."}, 400

        lista_pagadas = fetch_pagadas()

        #No hay ninguna cuota pagada.
        if not lista_pagadas:
            return {"Total": 0.0, "Detalle": []}, 200
        
        df = pd.DataFrame(lista_pagadas)

        #Necesario para evitar tener errores a la hora de usar "pd.Series.dt", ya que se
        #convierten todas las fechas a "datetime64" de Numpy.
        df['fechaPago'] = pd.to_datetime(df['fechaPago'], utc=True)

        df['year'] = df['fechaPago'].dt.year
        df['month'] = df['fechaPago'].dt.month

        #Filtro por año y mes
        sel = df[(df['year'] == anio_filtro) & (df['month'] == mes_filtro)]
        total = float(sel['montoPagado'].sum())

        detalle = (
            sel.loc[:, ['concepto', 'fechaPago', 'montoPagado', 'DNIAlumno']].assign(
                fechaPago=lambda d: d['fechaPago']
            )
            .to_dict(orient='records')
        )

        return {"Total": total, "Detalle": detalle}, 200

    except Exception as e:
        return {'error': str(e)}, 500


@require_auth(required_roles=['admin'])
def totales_por_mes_anio(request, uid=None, role=None):
    try:
        data = request.get_json(silent=True) or {}

        if not data or 'year' not in data:
            return {'error': "Se debe especificar un año."}, 400
        
        anio_filtro = data.get('year')

        if anio_filtro > datetime.now().year or anio_filtro < 1:
            return {'error': "Se debe especificar un numero de año válido a partir del año actual."}, 400
        
        lista_pagadas = fetch_pagadas()
        df = pd.DataFrame(lista_pagadas)

        df['fechaPago'] = pd.to_datetime(df['fechaPago'], utc=True)
        df['year']  = df['fechaPago'].dt.year
        df['month'] = df['fechaPago'].dt.month

        #Se filtra sólo el año
        df = df[df['year'] == anio_filtro]

        #Se agrupa por mes y se suma (por mes)
        grouped = df.groupby('month')['montoPagado'].sum()

        result = OrderedDict()

        for m in range(1, 13):
            nombre = MESES_REVRSD[m]
            result[nombre] = float(grouped.get(m, 0.0))
        

        #Se devuelve como dict mes→total (asegurando meses 1–12)
        return result, 200
    
    except Exception as e:
        return {'error': str(e)}, 500
