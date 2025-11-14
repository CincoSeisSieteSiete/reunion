from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import db
from datetime import datetime, timedelta
from datetime import date

def dashboard_rutas(request):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Usuario
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas
                FROM usuarios u
                WHERE u.id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            # Mostrar panel si no tiene fecha de nacimiento
            mostrar_panel_cumple = not user['fecha_nacimiento']

            # Guardar fecha si viene del form
            if request.method == 'POST' and 'fecha_nacimiento' in request.form:
                nueva_fecha = request.form['fecha_nacimiento']
                cursor.execute("UPDATE usuarios SET fecha_nacimiento = %s WHERE id = %s",
                               (nueva_fecha, session['user_id']))
                connection.commit()
                user['fecha_nacimiento'] = nueva_fecha
                mostrar_panel_cumple = False

            # Grupos
            cursor.execute("""
                SELECT g.*, 
                       (SELECT COUNT(*) FROM grupo_miembros WHERE grupo_id = g.id) as total_miembros
                FROM grupos g
                INNER JOIN grupo_miembros gm ON g.id = gm.grupo_id
                WHERE gm.usuario_id = %s
                ORDER BY g.fecha_creacion DESC
            """, (session['user_id'],))
            grupos = cursor.fetchall()

            # Medallas
            cursor.execute("""
                SELECT m.* FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (session['user_id'],))
            medallas = cursor.fetchall()

            # Cumpleaños del mes de los miembros de los grupos del usuario
            mes_actual = date.today().month
            cursor.execute("""
                SELECT u.nombre, u.fecha_nacimiento, g.nombre AS grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON gm.usuario_id = u.id
                INNER JOIN grupos g ON g.id = gm.grupo_id
                WHERE gm.grupo_id IN (
                    SELECT grupo_id FROM grupo_miembros WHERE usuario_id = %s
                )
                AND MONTH(u.fecha_nacimiento) = %s
                ORDER BY DAY(u.fecha_nacimiento) ASC
            """, (session['user_id'], mes_actual))
            cumpleanos_mes = cursor.fetchall()
            
            return render_template('dashboard.html', 
                                   user=user, grupos=grupos,
                                   medallas=medallas,
                                   mostrar_panel_cumple=mostrar_panel_cumple,
                                   cumpleanos_mes=cumpleanos_mes)
    finally:
        connection.close()