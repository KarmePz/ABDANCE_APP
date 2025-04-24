def asistencias(request):
    return 'hola asistencias', 200


def registrar_inasistencia(request):
    
    if request.method == 'POST':
        #add inasistencia alumno
        #la inasistencia registra la fecha y la hora en la que falto, tambien puede establecer la disciplina en la que fue la falta
        #
        print('Se debe registrar una inasistencia antes de este Print')
    elif request.method == 'DELETE':
        #delete inasistencia alumno por errores de usuario o anticipacion a falta
        
        print('Se debe Eliminar una inasistencia antes de este Print')
    return