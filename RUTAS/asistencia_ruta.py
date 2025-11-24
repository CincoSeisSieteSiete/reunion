from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
from QUERYS.queryGrupo import get_miembros_grupo, asistencias_hoy
from QUERYS.queryAsistencias import insertar_asistencia, presentes_del_dia
from QUERYS.queryPuntos import update_puntos

def tomar_asistencia_ruta(grupo_id):
    """
    Lógica para tomar asistencia de los miembros de un grupo.
    Solo accesible para líderes/administradores del grupo.
    """
    if request.method == 'POST':
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        asistentes = request.form.getlist('asistentes')  # Lista de user_id presentes
        
        # Obtener todos los miembros del grupo
        miembros = get_miembros_grupo(grupo_id)
        ids_miembros = [m['usuario_id'] for m in miembros]
        
        # Registrar asistencia para cada miembro
        for usuario in ids_miembros:
            presente = str(usuario) in asistentes
            
            # Insertar registro de asistencia
            insertar_asistencia(usuario, grupo_id, presente)
            
            # Si estuvo presente, actualizar sus puntos y racha
            if presente:
                update_puntos(usuario, grupo_id)
        
        flash('Asistencia registrada exitosamente', 'success')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id))
    
    # GET: Mostrar formulario de asistencia
    miembros = presentes_del_dia(grupo_id)
    asistentes_hoy = asistencias_hoy(grupo_id)
    
    return render_template(
        'gestionar/tomar_asistencia.html',
        grupo_id=grupo_id,
        miembros=miembros,
        asistentes_hoy=asistentes_hoy,
        fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
        tema=1
    )
