from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os

def register_rutas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        if not nombre or not email or not password or not fecha_nacimiento:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('register'))
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('El email ya está registrado', 'danger')
                    return redirect(url_for('register'))
                
                # Crear usuario con rol por defecto 'usuario'
                hashed_password = generate_password_hash(password)
                # Obtenemos el id del rol 'usuario'
                cursor.execute("SELECT id FROM roles WHERE nombre = 'usuario'")
                rol = cursor.fetchone()
                rol_id = rol['id'] if rol else 2  # fallback si no existe

                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, rol_id) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, email, hashed_password, fecha_nacimiento, rol_id)
                )
                connection.commit()
                flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
        finally:
            connection.close()
    
    return render_template('register.html')