from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from datetime import date
from DB.conexion import get_connection
from QUERYS.querysRegistro import user_exists, get_default_role_id

def register_rutas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        genero = request.form.get('genero_id')
        password = request.form.get('password')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        if not nombre or not email or not password or not fecha_nacimiento or not genero:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('register'))

        connection = get_connection()
        try:
            if user_exists(email):
                flash('El email ya está registrado', 'danger')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            rol_id = get_default_role_id()

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password, genero_id, fecha_nacimiento, rol_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nombre, email, hashed_password, genero, fecha_nacimiento, rol_id)
                )
                connection.commit()

            flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            flash('Error al registrar usuario', 'danger')
            return redirect(url_for('register'))
        finally:
            connection.close()

    # Si no es POST, solo mostrar formulario
    return render_template('inicio/register.html')
