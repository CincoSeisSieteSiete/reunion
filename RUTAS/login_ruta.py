from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from DB.conexion import get_connection
from QUERYS.queryLogin import get_usuario

def login_rutas():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        connection = get_connection()
        try:
            user = get_usuario(email)
                
            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session["logged"] = True
                session['user_id'] = user['id']
                session['user_name'] = user['nombre']
                session['tema'] = 1 if user['tema'] == b'\x01' else 0
                session['user_rol'] = user['rol']
                flash(f'Bienvenido, {user["nombre"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
        finally:
            connection.close()
    
    return render_template('inicio/login.html')
