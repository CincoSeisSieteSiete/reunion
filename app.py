from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter, util
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime, timedelta
import os
from FUNCIONES.Decoradores import login_required, admin_required, lideres_required

# ESTA ES LA FORMA CORRECTA
from RUTAS.dashboard_ruta import dashboard_rutas
from RUTAS.grupo_ruta import ver_grupo_ruta
from RUTAS.register_ruta import register_rutas
from RUTAS.login_ruta import login_rutas
from RUTAS.crear_grupo_ruta import crear_grupo_rutas
from RUTAS.unirse_grupo_ruta import unirse_grupo_rutas
from RUTAS.cumpleanos_ruta import cumpleanos_rutas
from RUTAS.ranking_ruta import ranking_global_rutas
from QUERYS.querysAdmin import es_admin
from QUERYS.queryPuntos import update_puntos, gestion_puntos_usuario
from QUERYS.queryGrupo import get_miembros_grupo, asistencias_hoy
from QUERYS.queryMedallas import agregar_medalla, asignar_medalla, eliminar_medalla, get_medallas, get_medallas_of_user
from QUERYS.queryUsuario import get_users_medallas, get_info
from QUERYS.queryAsistencias import get_asistencia_usuario, insertar_asistencia, presentes_del_dia

from RUTAS.configuraciones_usuarios_rutas import configuracion
from RUTAS.tema_ruta import cambiar_tema
from RUTAS.configuraciones_usuarios_rutas import configuraciones_usuarios_rutas
from JWT.JWT import verificar_y_renovar_token, eliminar_token, crear_access_token
from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity, set_access_cookies
import logging

app = Flask(__name__)

app.register_blueprint(configuraciones_usuarios_rutas)

app.secret_key = os.getenv('SECRET_KEY', 'Nioy')
app.permanent_session_lifetime = timedelta(days=10)
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30

limiter = Limiter(
    app=app,
    key_func=util.get_remote_address, # Usa la IP para la limitación
    default_limits=["200 per day", "50 per hour"] # Límites predeterminados
)

app.config['JWT_SECRET_KEY'] = 'jsabebJSKAEAVKHA1U3Y6HSHA'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Usa cookies en lugar de headers
app.config['JWT_COOKIE_SECURE'] = False  # True en producción con HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # Protección CSRF
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Previene CSRF
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
jwt = JWTManager(app)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/tema', methods=['GET', 'POST'])
def cambiar_tema_view():
    cambiar_tema()
    return redirect('/configuracion')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    return register_rutas()

@limiter.limit("5 per hour")
@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_rutas()

@app.route('/logout')
@eliminar_token
def logout():
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@verificar_y_renovar_token
def dashboard():
    if not session.get("logged"):
        return redirect("/login")
    return dashboard_rutas(request)

@app.route('/grupo/<int:grupo_id>')
@login_required
def ver_grupo(grupo_id):
    return ver_grupo_ruta(grupo_id)

@app.route('/crear_grupo', methods=['GET', 'POST'])
@limiter.limit("1 per hour")
@login_required
@lideres_required
@verificar_y_renovar_token
def crear_grupo():
    return crear_grupo_rutas()


@app.route('/unirse_grupo', methods=['GET', 'POST'])
@limiter.limit("10 per day")
@login_required
@verificar_y_renovar_token
def unirse_grupo():
    return unirse_grupo_rutas()

@app.route('/cumples/<int:id_grupo>')
@login_required
def cumpleanos(id_grupo):
    return cumpleanos_rutas(id_grupo)

# ==========================================================================================
@verificar_y_renovar_token
def actualizar_racha_y_puntos(usuario_id, grupo_id):
    """Actualiza la racha y puntos del usuario"""
    update_puntos(usuario_id, grupo_id)
    

@app.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
@login_required
@lideres_required
@verificar_y_renovar_token
def gestionar_puntos(grupo_id):
    
    if es_admin(grupo_id, session['user_id']):
        flash('No tienes permisos', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
                usuario_id = request.form.get('usuario_id')
                puntos = int(request.form.get('puntos', 0))
                accion = request.form.get('accion')
                
                puntos = puntos if accion == 'agregar' else -puntos
                gestion_puntos_usuario(puntos, usuario_id)
                flash('Puntos actualizados exitosamente', 'success')
                return redirect(url_for('gestionar_puntos', grupo_id=grupo_id))
    miembros = get_miembros_grupo(grupo_id)
            
    return render_template('gestionar/gestionar_puntos.html', grupo_id=grupo_id, miembros=miembros)
    



@app.route('/admin/medallas', methods=['GET', 'POST'])
@admin_required
@verificar_y_renovar_token
def gestionar_medallas():
    if request.method == 'POST':
        accion = request.form.get('accion')
                
        if accion == 'crear':
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            imagen = request.form.get('imagen')
            if not agregar_medalla(nombre,descripcion, imagen):
                flash('Fallo crear medalla', 'error')
            else:
                flash('Medalla creada exitosamente', 'success')
                    
        elif accion == 'asignar':
            usuario_id = request.form.get('usuario_id')
            medalla_id = request.form.get('medalla_id')
                                    
            if not asignar_medalla(usuario_id, medalla_id):
                flash('Fallo al asignar medalla', 'success')
            else:
                flash('Medalla asignada exitosamente', 'success')
                                    
        elif accion == 'eliminar':
            medalla_id = request.form.get('medalla_id')
            if not eliminar_medalla(medalla_id):
                flash('No se pudo eliminar la medalla', 'success')
            else:
                flash('Medalla eliminada exitosamente', 'success')
                
            return redirect(url_for('gestionar_medallas'))
            
        # Obtener todas las medallas
        medallas = get_medallas()
            
        # Obtener todos los usuarios
        usuarios = get_users_medallas()

            # 🖼️ Obtener imágenes del directorio static/medallas
        medallas_path = os.path.join(app.root_path, 'static', 'medallas')
        imagenes = [f for f in os.listdir(medallas_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
            
        return render_template(
                'gestionar/gestionar_medallas.html',
                medallas=medallas,
                usuarios=usuarios,
                imagenes=imagenes
            )

@app.route('/perfil')
@login_required
def perfil():
    user = get_info(session['user_id'])
    # Medallas del usuario
    medallas = get_medallas_of_user(session['user_id'])
    
    historial = get_asistencia_usuario(session['user_id'])
            
    return render_template('user_view/perfil.html', user=user, medallas=medallas, historial=historial)


@app.route('/ranking')
@login_required
@verificar_y_renovar_token
def ranking_global():
    return ranking_global_rutas()

@app.route('/subir_imagen_medalla', methods=['POST'])
@limiter.limit("3 per hour")
@verificar_y_renovar_token
def subir_imagen_medalla():
    imagen = request.files.get('imagen')
    nombre_imagen = request.form.get('nombre_imagen')
    if not imagen or not nombre_imagen:
        return "Error: faltan datos", 400
    # Obtener extensión original (.png, .jpg, etc.)
    extension = os.path.splitext(imagen.filename)[1]
    nuevo_nombre = f"{nombre_imagen}{extension}"
    ruta_carpeta = os.path.join(app.static_folder, 'medallas')
    os.makedirs(ruta_carpeta, exist_ok=True)
    ruta_archivo = os.path.join(ruta_carpeta, nuevo_nombre)
    imagen.save(ruta_archivo)
    return redirect(url_for('gestionar/gestionar_medallas'))

@app.route('/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
@lideres_required
@limiter.limit("2 per day")
@verificar_y_renovar_token
def tomar_asistencia(grupo_id):
    if request.method == 'POST':
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        asistentes = request.form.getlist('asistentes')  # Lista de user_id presentes

        # Obtener todos los miembros del grupo
        miembros = get_miembros_grupo(grupo_id)
        ids_miembros = [m['usuario_id'] for m in miembros]

        for usuario in ids_miembros:
            presente = str(usuario) in asistentes

            insertar_asistencia(usuario, grupo_id, presente)

            if presente:
                update_puntos(usuario, grupo_id)

        flash('Asistencia registrada exitosamente', 'success')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id))

    # GET: mostrar formulario
    miembros = presentes_del_dia(grupo_id)
    asistentes_hoy = asistencias_hoy(grupo_id)

    return render_template(
        'gestionar/tomar_asistencia.html',
        grupo_id=grupo_id,
        miembros=miembros,
        asistentes_hoy=asistentes_hoy,
        fecha_hoy=datetime.now().strftime('%Y-%m-%d')
    )


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Requiere el refresh token
def refresh():
    """
    Renueva el access token usando el refresh token
    """
    try:
        user_id = get_jwt_identity()
        
        # Crear nuevo access token
        new_access_token = crear_access_token(user_id)
        
        # Establecer nueva cookie
        response = jsonify({'mensaje': 'Token renovado'})
        set_access_cookies(response, new_access_token)
        
        logging.info(f"Token renovado para usuario: {user_id}")
        return response, 200
    except Exception as e:
        logging.error(f"Error al renovar token: {e}")
        return jsonify({'error': 'No se pudo renovar el token'}), 401

if __name__ == '__main__':
    # Ejecutar aplicación
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='127.0.0.1', port=5000)
