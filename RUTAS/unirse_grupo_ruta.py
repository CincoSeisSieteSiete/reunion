from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from RUTAS import register_ruta
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os

def unirse_grupo_rutas():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Buscar grupo por código
                cursor.execute("SELECT id FROM grupos WHERE codigo_invitacion = %s", (codigo,))
                grupo = cursor.fetchone()
                
                if not grupo:
                    flash('Código de invitación inválido', 'danger')
                    return redirect(url_for('unirse_grupo'))
                
                # Verificar si ya es miembro
                cursor.execute(
                    "SELECT id FROM grupo_miembros WHERE grupo_id = %s AND usuario_id = %s",
                    (grupo['id'], session['user_id'])
                )
                
                if cursor.fetchone():
                    flash('Ya eres miembro de este grupo', 'info')
                    return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
                
                # Agregar como miembro
                cursor.execute(
                    "INSERT INTO grupo_miembros (grupo_id, usuario_id) VALUES (%s, %s)",
                    (grupo['id'], session['user_id'])
                )
                
                # Registrar uso de invitación
                cursor.execute(
                    "INSERT INTO invitaciones (codigo, grupo_id, usado_por, fecha_uso) VALUES (%s, %s, %s, NOW())",
                    (codigo, grupo['id'], session['user_id'])
                )
                
                connection.commit()
                flash('Te has unido al grupo exitosamente', 'success')
                return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
        finally:
            connection.close()
    
    return render_template('unirse_grupo.html')