from flask import Flask, request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_init import db  # Firebase con base de datos inicializada
from datetime import datetime


#TODOS ESTOS METODOS DEBEN SER PROTEGIDOS MEDIANTE EL USO DE VERIFICACION DE TOKENS QUE SE ASIGNEN DESDE EL FRONTEND
#
#De otra manera cualquiera puede acceder a estos datos
#
#Verificar que se cumpla la autenticacion del token y el rol determinado
#


#CRUD DE DISCIPLINAS 
def disciplinas(request):
    if request.method == 'GET':
        try:
            data = request.json
            disciplina_id = data.get('disciplina_id')
            
            if not data or 'disciplina_id' not in data:
                #se deben devolver todas las disciplinas
                
                disciplinas_ref = db.collection('disciplinas')
                disciplinas = [doc.to_dict() for doc in disciplinas_ref.stream()]
                return jsonify(disciplinas), 200
                    
        
            #se debe devolver la disciplina que se pidio
            
            disciplina_ref = db.collection('disciplinas').document(disciplina_id)
            disciplina_doc = disciplina_ref.get()
            
            
            if disciplina_doc.exists:
                disciplina_data = disciplina_doc.to_dict()
                return jsonify(disciplina_data), 200
            else:
                return jsonify({'error':'Disciplina no encontrada'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500    
        
        #SE DEBE TRABAJAR TAMBIEN EN EL TEMA DE ALUMNOS DE LAS DISCIPLINAS 
            
    elif request.method == 'POST':
        #se debe crear una nueva disciplina
        return
    
    elif request.method == 'PUT':
        #se tiene que actualizar una disciplina segun los nuevos datos que se ingresen
        
        #actualizar edades
        #actualizar nombre
        #actualizar precios
        return
    
    elif request.method == 'DELETE':
        #se debe eliminar una disciplina segun el id especificado
        return
    else:
        return jsonify({'error':'Método no permitido'}), 405   

def parsearFecha(value_date):
    try:
        final_value = datetime.fromisoformat(value_date) if value_date else None
        return final_value
    except ValueError:
            return {'error': 'Formato de fecha inválido'}, 400 # formato de la fecha = YYYY-mm-ddThh:mm:ss.499588



def getAlumnosPorDisciplina(disciplina_id): #get de todos los alumnos anotados a determinada disciplina
    disciplina_ref = db.collection('disciplinas').document(disciplina_id)
    disciplina_doc = disciplina_ref.get()
    disciplina_data = disciplina_doc.to_dict()
    disciplina_name = disciplina_data.get('nombre')
    
    
    alumnos_ref = db.collection('disciplinas').document(disciplina_id).collection('alumnos')
    alumnos = [doc.to_dict() for doc in alumnos_ref.stream()]
    return jsonify({"nombre_disciplina": disciplina_name,
                    "alumnos":alumnos}), 200

def añadirAlumnoDisciplina(disciplina_id, dni_alumno): #metodo para añadir un dni de un alumno a una disciplina particular
    return


def eliminarAlumnoDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un dni de un alumno de una disciplina particular
    return



def getProfesoresPorDisciplina(disciplina_id): #get de todos los profesores anotados a determinada disciplina
    return

def añadirProfesorDisciplina(disciplina_id, dni_alumno): #metodo para añadir un dni de un profesor a una disciplina particular
    return


def eliminarProfesorDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un dni de un Profesor de una disciplina particular
    return



def getHorariosPorDisciplina(disciplina_id):#get de todos los horarios asignados a determinada disciplina
    return

def añadirHorarioDisciplina(disciplina_id, dni_alumno): #metodo para añadir un horario a una disciplina particular
    return


def eliminarHorarioDisciplina(disciplina_id, dni_alumno):#metodo para eliminar un horario de una disciplina particular
    return

