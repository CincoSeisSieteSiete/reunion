from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from RUTAS import register_ruta
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os

def crear_grupo_rutas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre del grupo es obligatorio', 'danger')
            return redirect(url_for('crear_grupo'))
        
        # Generar código de invitación único
        codigo = secrets.token_urlsafe(8)
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO grupos (nombre, descripcion, admin_id, codigo_invitacion) VALUES (%s, %s, %s, %s)",
                    (nombre, descripcion, session['user_id'], codigo)
                )
                grupo_id = cursor.lastrowid
                
                # Agregar al admin como miembro del grupo
                cursor.execute(
                    "INSERT INTO grupo_miembros (grupo_id, usuario_id) VALUES (%s, %s)",
                    (grupo_id, session['user_id'])
                )
                
                connection.commit()
                flash(f'Grupo creado exitosamente. Código de invitación: {codigo}', 'success')
                return redirect(url_for('ver_grupo', grupo_id=grupo_id))
        finally:
            connection.close()
    
    return render_template('crear_grupo.html')