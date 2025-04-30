from flask import Flask, request, jsonify, Response
import json
import functions_framework
import firebase_admin
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime



def asistencias(request):
    data = request.json 
    if request.method == 'GET':
        #mostrar todas las asistencias de un alumno 
        #se debe pedir id  del usuario
        pass
    
    
    return 'hola asistencias', 200


def registrar_inasistencia(request):
    data = request.json  #para registrar la inasistencia se requiere el dni del usuario al que se le va a registrar dicha inasistencia
    
    
    if request.method == 'POST':
        #add inasistencia alumno
        #la inasistencia registra la fecha y la hora en la que falto, tambien puede establecer la disciplina en la que fue la falta
        #se guarda como una subcoleccion de usuario con rol alumno
        #se debe crear una nueva inasistencia
        inasistencia_user_dni = data.get("dni_usuario")
        inasistencia_fecha = data.get("fecha") #debe ser la fecha de HOY 
        inasistencia_justificacion = data.get("justificada")
        
        if not inasistencia_justificacion or not inasistencia_fecha or not inasistencia_user_dni:
            return jsonify({'error':'Faltan datos. Revise la justificacion, fecha, usuario'}), 400
        
        #se busca en la base de datos el usuario al que corresponde la inasistencia y se agrega
        user_ref = db.collection('usuarios').document(inasistencia_user_dni)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'error':'No se encontro el usuario especificado.'}), 404
        
        inasistencia_ref = user_ref.collection('inasistencias').document()
        
        #se genera el id 
        inasistencia_id = inasistencia_ref.id
        data['id'] = inasistencia_id
        
        
        #se guarda el documento con el id generado
        inasistencia_ref.set(data)
        return jsonify({'message': 'Inasistencia registrada exitosamente'}), 201
        
        print('Se debe registrar una inasistencia antes de este Print')
    elif request.method == 'DELETE':
        #delete inasistencia alumno por errores de usuario o anticipacion a falta
        if not data or 'id_inasistencia' not in data or 'dni_usuario' not in data :
            return jsonify({'error': ' Ingrese el id del usuario o la inasistencia correspondiente'}), 400 #######
        
        user_ref = db.collection('usuarios').document(data['dni_usuario'])
        inasistencia_ref = user_ref.collection('inasistencias').document(data['id_inasistencia'])
        inasistencia_doc = inasistencia_ref.get()
        
        if not inasistencia_doc.exists:
            return jsonify({'error': 'No se encontro la inasistencia especificada'}), 404
        
        #se elimina la inasistencia de la firestore
        inasistencia_ref.delete()
        return jsonify({'message':'Inasistencia eliminada correctamente'}), 200
        
    return


def eliminar_inasistencias(request):
    if request.method == 'DELETE':
        pass
    return