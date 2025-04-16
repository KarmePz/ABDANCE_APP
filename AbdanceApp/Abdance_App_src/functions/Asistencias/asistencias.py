def asistencias(request):
    return 'hola asistencias', 200


def registrar_inasistencia(request):
    
    if request.method == 'POST':
        #add inasistencia alumno
        print('Se debe registrar una inasistencia antes de este Print')
    elif request.method == 'DELETE':
        #add inasistencia alumno
        print('Se debe Eliminar una inasistencia antes de este Print')
    return