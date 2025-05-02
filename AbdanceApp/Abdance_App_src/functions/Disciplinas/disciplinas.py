from flask import Flask, request, jsonify, Response
import json
import functions_framework
import firebase_admin
from collections import OrderedDict
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime
from functions.Usuarios.auth_decorator import require_auth

#TODOS ESTOS METODOS DEBEN SER PROTEGIDOS MEDIANTE EL USO DE VERIFICACION DE TOKENS QUE SE ASIGNEN DESDE EL FRONTEND
#
#De otra manera cualquiera puede acceder a estos datos
#
#Verificar que se cumpla la autenticacion del token y el rol determinado
#


#CRUD DE DISCIPLINAS 
def disciplinas(request):
    if request.method == 'GET':
        return getDisciplinas(request)
        #SE DEBE TRABAJAR TAMBIEN EN EL TEMA DE ALUMNOS DE LAS DISCIPLINAS 
            
    elif request.method == 'POST':
        return postDisciplinas(request)
        
    
    elif request.method == 'PUT':
        return putDisciplinas(request)
    
    elif request.method == 'DELETE':
        return deleteDisciplina(request)
    
    else:
        return jsonify({'error':'Método no permitido'}), 405   

def parsearFecha(value_date):
    try:
        final_value = datetime.fromisoformat(value_date) if value_date else None
        return final_value
    except ValueError:
            return {'error': 'Formato de fecha inválido'}, 400 # formato de la fecha = YYYY-mm-ddThh:mm:ss.499588

def ordenar_datos_disciplina(data_disciplina, alumnos_inscriptos=None):   # Armamos el diccionario con orden especifico para hacerlo mas legible
    disciplina_data = OrderedDict()
    disciplina_data["disciplina_id"] = data_disciplina.get("id")
    disciplina_data["nombre"] = data_disciplina.get("nombre")
    disciplina_data["edadMinima"] = data_disciplina.get("edadMinima")
    disciplina_data["edadMaxima"] = data_disciplina.get("edadMaxima")
    disciplina_data["precios"] = data_disciplina.get("precios")
    
    if alumnos_inscriptos is not None:
        disciplina_data["alumnos_inscriptos"] = alumnos_inscriptos
        
    return disciplina_data


def getAlumnosPorDisciplina(disciplina_id): #get de todos los alumnos anotados a determinada disciplina
    alumnos_ref = db.collection('disciplinas').document(disciplina_id).collection('alumnos')
    alumnos = [doc.to_dict() for doc in alumnos_ref.stream()]
    return alumnos
    #return jsonify({"nombre_disciplina": disciplina_name,
    #               "alumnos_inscriptos":alumnos}), 200

def añadirAlumnoDisciplina(disciplina_id, dni_alumno): #metodo para añadir un dni de un alumno a una disciplina particular
    return


def eliminarAlumnoDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un dni de un alumno de una disciplina particular
    return



def getProfesoresPorDisciplina(disciplina_id): #get de todos los profesores anotados a determinada disciplina
    profesores_ref = db.collection('disciplinas').document(disciplina_id).collection('profesores')
    profesores = [doc.to_dict() for doc in profesores_ref.stream()]
    return profesores
    

def añadirProfesorDisciplina(disciplina_id, dni_alumno): #metodo para añadir un dni de un profesor a una disciplina particular
    return


def eliminarProfesorDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un dni de un Profesor de una disciplina particular
    return



def getHorariosPorDisciplina(disciplina_id):#get de todos los horarios asignados a determinada disciplina
    horarios_ref = db.collection('disciplinas').document(disciplina_id).collection('horarios')
    horarios = [doc.to_dict() for doc in horarios_ref.stream()]
    return horarios

def añadirHorarioDisciplina(disciplina_id, dni_alumno): #metodo para añadir un horario a una disciplina particular
    return


def eliminarHorarioDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un horario de una disciplina particular
    return

@require_auth(required_roles=['alumno', 'profesor', 'admin'])
def getDisciplinas(request, uid=None, role=None):
    try:
        data = request.json
        disciplina_id = data.get('disciplina_id')
        
        
        if not data or 'disciplina_id' not in data:# si no se especifica un id determinado se ejecuta lo siguiente
            #se deben devolver todas las disciplinas
            disciplinas = []
            disciplinas_ref = db.collection('disciplinas')
            
            for doc in disciplinas_ref.stream():
                data_disciplina = doc.to_dict()
                doc_disciplina_id = doc.id
                
                alumnos_inscriptos_id = getAlumnosPorDisciplina(doc_disciplina_id)
                #agregar horarios y profesores de la misma manera
                disciplina_data = ordenar_datos_disciplina(data_disciplina, alumnos_inscriptos_id)
                
                disciplinas.append(disciplina_data)
                
            #se deben devolver todos los alumnos por cada disciplina: 
            return Response(json.dumps(disciplinas), mimetype='application/json'), 200
                
    
        #se debe devolver la disciplina que se pidio si se especifica un id
        
        disciplina_ref = db.collection('disciplinas').document(disciplina_id)
        disciplina_doc = disciplina_ref.get()
        
        
        if disciplina_doc.exists: #si existe el id de la disciplina se extraen los datos como diccionario
            data_disciplina = disciplina_doc.to_dict()
            alumnos_inscriptos = getAlumnosPorDisciplina(disciplina_id)
            
            disciplina_data = ordenar_datos_disciplina(data_disciplina, alumnos_inscriptos)
            
            return Response(json.dumps(disciplina_data), mimetype='application/json'), 200
        else:
            return jsonify({'error':'Disciplina no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

@require_auth(required_roles=['admin'])
def postDisciplinas(request, uid=None, role=None):
    
    data_disciplina = request.json
        #se debe crear una nueva disciplina
    disciplina_name = data_disciplina.get("nombre")
    disciplina_minAge = data_disciplina.get("edadMinima")
    disciplina_maxAge = data_disciplina.get("edadMaxima")
    disciplina_price = data_disciplina.get("precios") #precios debe ser un mapa
    
    if not disciplina_name or not disciplina_minAge or not disciplina_maxAge or not disciplina_price:
        return jsonify({'error':'Faltan datos. Revise nombre, edad minima, edad maxima, precios'}), 400
    
    #si todos los datos existen se añaden a la base de datos
    disciplinas_ref = db.collection("disciplinas").document()
    
    #generar el id aleatorio
    disciplina_id = disciplinas_ref.id
    data_disciplina['id'] = disciplina_id
    
    #guardar documento con el id
    disciplinas_ref.set(data_disciplina)
    
    return jsonify({'message': 'Disciplina registrada exitosamente'}), 201

@require_auth(required_roles=['admin'])
def putDisciplinas(request, uid=None, role=None):
    #se tiene que actualizar una disciplina segun los nuevos datos que se ingresen
    #actualizar edades
    #actualizar nombre
    #actualizar precios
    data = request.json 
    
    if not data or 'id' not in data:
        return jsonify({'error': ' Ingrese el id de la disciplina correspondiente'}), 400 #######
    
    
    disciplina_ref = db.collection('disciplinas').document(data['id'])
    disciplina_doc = disciplina_ref.get()
    disciplina_data = disciplina_doc.to_dict()
    
    #control de errores 
    if not disciplina_doc.exists:
        return jsonify({'error': 'No se encontro la disciplina especificada'}), 404
    
    disciplina_ref.update(data)
    return jsonify({"message":"usuario Actualizado",
                    "id": disciplina_data.get('id'), 
                    "nombre disciplina modificado" :disciplina_data.get('nombre')}), 200

@require_auth(required_roles=['admin'])
def deleteDisciplina(request, uid=None, role=None):
    #se debe eliminar una disciplina segun el id especificado
    data = request.json 
    
    if not data or 'id' not in data:
        return jsonify({'error': ' Ingrese el id de la disciplina correspondiente'}), 400 #######
    
    disciplina_ref = db.collection('disciplinas').document(data['id'])
    disciplina_doc = disciplina_ref.get()
    disciplina_data = disciplina_doc.to_dict()
    
    #control de errores 
    if not disciplina_doc.exists:
        return jsonify({'error': 'No se encontro la disciplina especificada'}), 404
    
    #eliminacion de BD firestore
    disciplina_ref.delete()
    return jsonify({'message':'Disciplina eliminada correctamente'}), 200