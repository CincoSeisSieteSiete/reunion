from flask import render_template, request, redirect, url_for, session, flash
from QUERYS.querysAdmin import es_admin, es_lider_global
from QUERYS.queryPuntos import gestion_puntos_usuario
from QUERYS.queryGrupo import get_miembros_grupo

def gestionar_puntos_ruta(grupo_id):
    """
    Lógica para gestionar puntos de los miembros de un grupo.
    Solo accesible para administradores del grupo o líderes globales.
    """
    # Verificar si el usuario es admin del grupo o tiene rol de líder/admin global
    if not (es_admin(grupo_id, session['user_id']) or es_lider_global(session['user_id'])):
        flash('No tienes permisos para gestionar puntos', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        puntos = int(request.form.get('puntos', 0))
        accion = request.form.get('accion')
        
        # Si la acción es restar, convertir puntos a negativo
        puntos = puntos if accion == 'agregar' else -puntos
        
        # Actualizar puntos del usuario
        gestion_puntos_usuario(puntos, usuario_id)
        
        flash('Puntos actualizados exitosamente', 'success')
        return redirect(url_for('gestionar_puntos', grupo_id=grupo_id))
    
    # GET: Obtener miembros del grupo
    miembros = get_miembros_grupo(grupo_id)
    
    return render_template('gestionar/gestionar_puntos.html', 
                          grupo_id=grupo_id, 
                          miembros=miembros,
                          tema=1)
