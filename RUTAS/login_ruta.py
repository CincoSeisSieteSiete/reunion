from flask import render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import check_password_hash
from QUERYS.queryLogin import get_usuario
from MODELS.Usuario import Usuario
from JWT.JWT import crear_access_token, crear_refresh_token
from DB.conexion import get_connection  # tu db.py

# ===============================
#     OBTENER NOMBRE DEL ROL
# ===============================
def get_rol_name(rol_id):
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT nombre FROM roles WHERE id = %s"
            cursor.execute(sql, (rol_id,))
            result = cursor.fetchone()
            if result:
                return result['nombre']   # ✅ Diccionario
            return None
    finally:
        conexion.close()


# ===============================
#            LOGIN
# ===============================
def login_rutas():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        # Buscar usuario por email
        user = get_usuario(email)

        # Validar credenciales
        if user and check_password_hash(user.password, password):

            # Obtener nombre del rol
            nombre_rol = get_rol_name(user.rol_id)

            # Guardar sesión
            session.permanent = True
            session['logged'] = True
            session['user_id'] = user.id
            session['user_name'] = user.nombre
            session['tema'] = 1 if user.tema == b'\x01' else 0
            session['rol_id'] = str(user.rol_id)
            session['rol_name'] = nombre_rol

            flash(f'Bienvenido, {user.nombre}!', 'success')

            # Generar tokens JWT
            access_token = crear_access_token(user.id)
            refresh_token = crear_refresh_token(user.id)

            # Respuesta + cookies
            respuesta = make_response(redirect(url_for('dashboard')))
            respuesta.set_cookie('access_token', access_token, max_age=2592000, httponly=True, samesite='Lax')
            respuesta.set_cookie('refresh_token', refresh_token, max_age=2592000, httponly=True, samesite='Lax')

            return respuesta

        else:
            flash('Email o contraseña incorrectos', 'danger')

    return render_template('inicio/login.html')
