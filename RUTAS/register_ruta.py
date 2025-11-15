from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os
from QUERYS.querysRegistro import user_exists, get_default_role_id

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
            exists = user_exists(email)
            if exists:
                flash('El email ya está registrado', 'danger')
                return redirect(url_for('register'))
                            
            # Crear usuario con rol por defecto 'usuario'
            hashed_password = generate_password_hash(password)
            # Obtenemos el id del rol 'usuario'
            rol_id = get_default_role_id()

            if not rol_id:
                flash('Error al asignar el rol por defecto', 'danger')
                return redirect(url_for('register'))
            flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        finally:
            connection.close()
    
    return render_template('register.html')