from flask import render_template, request, redirect, url_for, session, flash
import db
from datetime import datetime, timedelta
from datetime import date
from QUERYS.queryGrupo import get_esta_grupo, get_grupo_info, get_raking_grupo

def ver_grupo_ruta(grupo_id):
    """
    Contiene la lógica para mostrar la página de un grupo específico.
    Verifica la membresía, obtiene datos del grupo y el ranking.
    """
    connection = db.get_connection()
    try:    
        # Verificar si el usuario es miembro del grupo
        is_grupo_member = get_esta_grupo(grupo_id, session['user_id'])
            
        if not is_grupo_member:
            flash('No eres miembro de este grupo', 'danger')
            return redirect(url_for('dashboard'))
            
        # Obtener información del grupo
        grupo = get_grupo_info(grupo_id)
            
            # Si el grupo no existe, redirigir
        if not grupo:
            flash('El grupo solicitado no existe.', 'danger')
            return redirect(url_for('dashboard'))

        # Obtener ranking del grupo
        ranking = get_raking_grupo(grupo_id)
            
        # Verificar si el usuario es admin del grupo
        es_admin = grupo['admin_id'] == session['user_id']
            
        return render_template('grupo.html', grupo=grupo, grupo_id=grupo_id, ranking=ranking, es_admin=es_admin)
    finally:
        connection.close()