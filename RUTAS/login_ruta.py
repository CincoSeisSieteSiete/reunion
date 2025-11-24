from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from QUERYS.queryLogin import get_usuario
from QUERYS.queryRol import get_rol_name
from MODELS.Usuario import Usuario
from JWT.JWT import crear_access_token, crear_refresh_token

def login_rutas():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_usuario(email)
                
        if user and check_password_hash(user.password, password):
            #Otra query para obtener el nombre del rol
            nombre_rol = get_rol_name(user.rol_id)
            session.permanent = True
            session["logged"] = True
            session['user_id'] = user.id
            session['user_name'] = user.nombre
            session['tema'] = 1 if user.tema == b'\x01' else 0
            session['user_rol'] = nombre_rol
            flash(f'Bienvenido, {user.nombre}!', 'success')
            access_token = crear_access_token(user.id)
            refresh_token = crear_refresh_token(user.id)

            respuesta = make_response(redirect(url_for('dashboard')))
            # max_age en segundos: 30 días = 30 * 24 * 60 * 60 = 2592000
            respuesta.set_cookie('access_token', access_token, max_age=2592000, httponly=True, samesite='Lax')
            respuesta.set_cookie('refresh_token', refresh_token, max_age=2592000, httponly=True, samesite='Lax')
            return respuesta
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('inicio/login.html')
