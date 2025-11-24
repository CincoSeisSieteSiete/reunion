from flask import render_template, session
from QUERYS.queryUsuario import get_info
from QUERYS.queryMedallas import get_medallas_of_user
from QUERYS.queryAsistencias import get_asistencia_usuario

def perfil_ruta():
    """
    Lógica para mostrar el perfil del usuario actual.
    Incluye información personal, medallas y historial de asistencias.
    """
    user_id = session['user_id']
    
    # Obtener información del usuario
    user = get_info(user_id)
    
    # Obtener medallas del usuario
    medallas = get_medallas_of_user(user_id)
    
    # Obtener historial de asistencias
    historial = get_asistencia_usuario(user_id)
    
    return render_template('user_view/perfil.html', 
                          user=user, 
                          medallas=medallas, 
                          historial=historial,
                          tema=1)
