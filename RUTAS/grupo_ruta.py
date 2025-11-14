from flask import render_template, request, redirect, url_for, session, flash
import db
from datetime import datetime, timedelta
from datetime import date

def ver_grupo_ruta(grupo_id):
    """
    Contiene la lógica para mostrar la página de un grupo específico.
    Verifica la membresía, obtiene datos del grupo y el ranking.
    """
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el usuario es miembro del grupo
            cursor.execute("""
                SELECT COUNT(*) as es_miembro 
                FROM grupo_miembros 
                WHERE grupo_id = %s AND usuario_id = %s
            """, (grupo_id, session['user_id']))
            
            if cursor.fetchone()['es_miembro'] == 0:
                flash('No eres miembro de este grupo', 'danger')
                return redirect(url_for('dashboard'))
            
            # Obtener información del grupo
            cursor.execute("""
                SELECT g.*, u.nombre as admin_nombre
                FROM grupos g
                INNER JOIN usuarios u ON g.admin_id = u.id
                WHERE g.id = %s
            """, (grupo_id,))
            grupo = cursor.fetchone()
            
            # Si el grupo no existe, redirigir
            if not grupo:
                flash('El grupo solicitado no existe.', 'danger')
                return redirect(url_for('dashboard'))

            # Obtener ranking del grupo
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND grupo_id = %s AND presente = TRUE) as asistencias_grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.puntos DESC, u.racha DESC
            """, (grupo_id, grupo_id))
            ranking = cursor.fetchall()
            
            # Verificar si el usuario es admin del grupo
            es_admin = grupo['admin_id'] == session['user_id']
            
            return render_template('grupo.html', grupo=grupo, grupo_id=grupo_id, ranking=ranking, es_admin=es_admin)
    finally:
        connection.close()