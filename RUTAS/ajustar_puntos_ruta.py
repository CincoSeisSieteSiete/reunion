from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os

def ajustar_puntos_rutas(grupo_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar permisos
            cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
            grupo = cursor.fetchone()
            
            if not grupo or grupo['admin_id'] != session['user_id']:
                flash('No tienes permisos', 'danger')
                return redirect(url_for('dashboard'))
            
            if request.method == 'POST':
                usuario_id = request.form.get('usuario_id')
                puntos = int(request.form.get('puntos', 0))
                accion = request.form.get('accion')
                
                if accion == 'agregar':
                    cursor.execute("UPDATE usuarios SET puntos = puntos + %s WHERE id = %s", (puntos, usuario_id))
                elif accion == 'quitar':
                    cursor.execute("UPDATE usuarios SET puntos = GREATEST(0, puntos - %s) WHERE id = %s", (puntos, usuario_id))
                
                connection.commit()
                flash('Puntos actualizados exitosamente', 'success')
                return redirect(url_for('gestionar_puntos', grupo_id=grupo_id))
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            miembros = cursor.fetchall()
            
            return render_template('gestionar_puntos.html', grupo_id=grupo_id, miembros=miembros)
    finally:
        connection.close()
