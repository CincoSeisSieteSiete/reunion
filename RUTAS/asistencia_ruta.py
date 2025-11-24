from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from QUERYS.queryGrupo import get_miembros_grupo, asistencias_hoy
from QUERYS.queryAsistencias import insertar_asistencia, presentes_del_dia, get_asistencia_por_fecha
from QUERYS.queryPuntos import update_puntos, remove_puntos
from QUERYS.querysAdmin import es_admin, es_lider_global

def tomar_asistencia_ruta(grupo_id):
    """
    Lógica para tomar asistencia de los miembros de un grupo.
    Solo accesible para líderes/administradores del grupo.
    """
    # Verificar permisos
    if not (es_admin(grupo_id, session['user_id']) or es_lider_global(session['user_id'])):
        flash('No tienes permisos para tomar asistencia', 'danger')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id))
    if request.method == 'POST':
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        asistentes = request.form.getlist('asistentes')  # Lista de user_id presentes
        
        # Obtener todos los miembros del grupo
        miembros = get_miembros_grupo(grupo_id)
        ids_miembros = [m['id'] for m in miembros]
        
        # Registrar asistencia para cada miembro
        for usuario in ids_miembros:
            presente_ahora = str(usuario) in asistentes
            
            # Verificar si ya existía asistencia para esta fecha
            asistencia_anterior = get_asistencia_por_fecha(usuario, grupo_id, fecha)
            
            # Debug: Ver qué encontramos
            print(f"DEBUG - Usuario {usuario}, Fecha {fecha}")
            print(f"  Presente ahora: {presente_ahora}")
            print(f"  Asistencia anterior: {asistencia_anterior}")
            
            # Insertar o actualizar registro de asistencia
            insertar_asistencia(usuario, grupo_id, presente_ahora, fecha)
            
            # Solo dar puntos si:
            # 1. No existía asistencia antes Y ahora está presente
            # 2. Existía como ausente Y ahora está presente
            debe_dar_puntos = presente_ahora and (
                asistencia_anterior is None or 
                not asistencia_anterior.get('presente', False)
            )
            
            # Quitar puntos si:
            # 1. Existía como presente Y ahora está ausente
            debe_quitar_puntos = (
                not presente_ahora and 
                asistencia_anterior is not None and 
                asistencia_anterior.get('presente', False)
            )
            
            print(f"  Debe dar puntos: {debe_dar_puntos}")
            print(f"  Debe quitar puntos: {debe_quitar_puntos}")
            
            if debe_dar_puntos:
                update_puntos(usuario, grupo_id)
            
            if debe_quitar_puntos:
                remove_puntos(usuario, grupo_id)
        
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
