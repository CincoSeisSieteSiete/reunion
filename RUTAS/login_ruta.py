from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db
from QUERYS.queryLogin import get_usuario

def login_rutas():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        connection = db.get_connection()
        try:
            user = get_usuario(email)
                
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['nombre']
                session['user_rol'] = user['rol']  # ahora sí existe
                flash(f'Bienvenido, {user["nombre"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
        finally:
            connection.close()
    
    return render_template('login.html')