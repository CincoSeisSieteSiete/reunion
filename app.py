from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
from werkzeug.middleware.proxy_fix import ProxyFix
from FUNCIONES.Decoradores import login_required, admin_required, lideres_required, grupo_admin_required

# IMPORTAR RUTAS
from RUTAS import admin_ruta
from RUTAS.dashboard_ruta import dashboard_rutas
from RUTAS.grupo_ruta import ver_grupo_ruta
from RUTAS.register_ruta import register_rutas
from RUTAS.login_ruta import login_rutas
from RUTAS.crear_grupo_ruta import crear_grupo_rutas
from RUTAS.unirse_grupo_ruta import unirse_grupo_rutas
from RUTAS.cumpleanos_ruta import cumpleanos_rutas
from RUTAS.ranking_ruta import ranking_global_rutas
from RUTAS.editar_rol import editar_rol
from RUTAS.configuraciones_usuarios_rutas import configuracion, configuraciones_usuarios_rutas
from RUTAS.tema_ruta import cambiar_tema
from RUTAS.ajustar_puntos_ruta import gestionar_puntos_ruta
from RUTAS.gestionar_medallas_ruta import gestionar_medallas_ruta
from RUTAS.perfil_ruta import perfil_ruta
from RUTAS.asistencia_ruta import tomar_asistencia_ruta
from RUTAS.subir_imagen_ruta import subir_imagen_medalla_ruta
from RUTAS.admin_ruta import admin_ruta
from RUTAS.JWT_ruta import refresh_ruta
from JWT.JWT import verificar_y_renovar_token, eliminar_token, crear_access_token, crear_refresh_token
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import  JWTManager, jwt_required
import logging

app = Flask(__name__)

# Load environment variables from .env if present
load_dotenv()
# Configure OAuthlib transport security:
# - Respect explicit OAUTHLIB_INSECURE_TRANSPORT env var if set
# - Otherwise allow insecure transport in development via FLASK_ENV/FLASK_DEBUG or ALLOW_INSECURE_OAUTH
insecure_env = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
if insecure_env is not None:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = insecure_env
else:
    allow_dev = os.environ.get('ALLOW_INSECURE_OAUTH', '').lower() in ('1', 'true', 'yes')
    flask_env_dev = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Correct proxy headers when running behind PythonAnywhere / reverse proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.register_blueprint(configuraciones_usuarios_rutas)
app.secret_key = 'una_clave_secreta_larga_y_unica' # ¡CRUCIAL!
app.permanent_session_lifetime = timedelta(days=10)
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30

limiter = Limiter(
    app=app,
    key_func=get_remote_address, # Usa la IP para la limitación
    default_limits=["200 per day", "50 per hour"] # Límites predeterminados
)

app.config['JWT_SECRET_KEY'] = 'jsabebJSKAEAVKHA1U3Y6HSHA'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Usa cookies en lugar de headers
app.config['JWT_COOKIE_SECURE'] = True  # True en producción con HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False    # Protección CSRF
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Previene CSRF
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
jwt = JWTManager(app)

logging.basicConfig(level=logging.INFO)

# Exponer variables de entorno FB a templates
try:
    import CONFIGURACION.config as app_config
except Exception:
    # Si falla la importación (ej. Render), creamos un objeto dummy
    class Config: pass
    app_config = Config()

# Cargar configuración con fallback a variables de entorno
app_config.FACEBOOK_CLIENT_ID = getattr(app_config, 'FACEBOOK_CLIENT_ID', os.environ.get('FACEBOOK_CLIENT_ID'))
app_config.FACEBOOK_CLIENT_SECRET = getattr(app_config, 'FACEBOOK_CLIENT_SECRET', os.environ.get('FACEBOOK_CLIENT_SECRET'))
app_config.FACEBOOK_API_VERSION = getattr(app_config, 'FACEBOOK_API_VERSION', os.environ.get('FACEBOOK_API_VERSION', 'v15.0'))

app.jinja_env.globals.update(FACEBOOK_CLIENT_ID=app_config.FACEBOOK_CLIENT_ID, FACEBOOK_API_VERSION=app_config.FACEBOOK_API_VERSION)

# -------------------
# OAuth / Facebook
# -------------------
oauth = OAuth(app)
if app_config.FACEBOOK_CLIENT_ID and app_config.FACEBOOK_CLIENT_SECRET:
    fb_version = app_config.FACEBOOK_API_VERSION or 'v15.0'
    oauth.register(
        name='facebook',
        client_id=app_config.FACEBOOK_CLIENT_ID,
        client_secret=app_config.FACEBOOK_CLIENT_SECRET,
        authorize_url=f'https://www.facebook.com/{fb_version}/dialog/oauth',
        access_token_url=f'https://graph.facebook.com/{fb_version}/oauth/access_token',
        api_base_url=f'https://graph.facebook.com/{fb_version}/',
        client_kwargs={'scope': 'email public_profile'}
    )
else:
    logging.warning('Facebook OAuth not configured: FACEBOOK_CLIENT_ID or FACEBOOK_CLIENT_SECRET is missing.')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/terminos')
def terminos():
    return render_template('terminos.html')


@app.route('/tema', methods=['GET', 'POST'])
def cambiar_tema_view():
    cambiar_tema()
    return redirect('/configuracion')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    return register_rutas()

@limiter.limit("10 per hour")
@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_rutas()


@app.route('/login/facebook')
def login_facebook():
    if not app_config.FACEBOOK_CLIENT_ID or not app_config.FACEBOOK_CLIENT_SECRET:
        flash('Facebook OAuth no está configurado en el servidor.', 'danger')
        return redirect(url_for('login'))
    redirect_uri = url_for('auth_facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@app.route('/debug/facebook_redirect_uri')
def debug_facebook_redirect_uri():
    # Returns the exact redirect URI used by the app so you can add it to Facebook app settings
    try:
        uri = url_for('auth_facebook_callback', _external=True)
    except Exception:
        uri = '/auth/facebook/callback'
    return jsonify({'redirect_uri': uri})


@app.route('/auth/facebook/callback')
def auth_facebook_callback():
    token = None
    try:
        token = oauth.facebook.authorize_access_token()
    except Exception as e:
        logging.exception('Error obtaining Facebook access token')
        flash('No se pudo autenticar con Facebook (error en el servidor).', 'danger')
        return redirect(url_for('login'))

    # Obtener perfil
    try:
        resp = oauth.facebook.get('me?fields=id,name,email,picture')
        resp.raise_for_status()
        userinfo = resp.json()
    except Exception as e:
        logging.exception('Error fetching Facebook profile')
        flash('No se pudieron obtener datos del perfil de Facebook (error en servidor).', 'danger')
        return redirect(url_for('login'))

    from QUERYS.queryLogin import get_usuario
    from QUERYS.querysRegistro import create_user
    from MODELS.Usuario import Usuario
    from JWT.JWT import crear_access_token, crear_refresh_token

    email = userinfo.get('email')
    nombre = userinfo.get('name') or email.split('@')[0]

    user = get_usuario(email)
    if not user:
        import secrets
        random_pw = secrets.token_urlsafe(16)
        nuevo = Usuario(nombre=nombre, email=email, password=random_pw)
        created = create_user(nuevo)
        if not created:
            flash('No se pudo crear el usuario a partir de Facebook.', 'danger')
            return redirect(url_for('login'))
        user = get_usuario(email)

    # Iniciar sesión
    nombre_rol = None
    try:
        from RUTAS.login_ruta import get_rol_name
        nombre_rol = get_rol_name(user.rol_id)
    except Exception:
        nombre_rol = None

    session.permanent = True
    session['logged'] = True
    session['user_id'] = user.id
    session['user_name'] = user.nombre
    session['tema'] = 1 if user.tema == b'\x01' else 0
    session['rol_id'] = str(user.rol_id)
    session['rol_name'] = nombre_rol

    access_token = crear_access_token(user.id)
    refresh_token = crear_refresh_token(user.id)

    respuesta = make_response(redirect(url_for('dashboard')))
    respuesta.set_cookie('access_token', access_token, max_age=2592000, httponly=True, samesite='Lax')
    respuesta.set_cookie('refresh_token', refresh_token, max_age=2592000, httponly=True, samesite='Lax')
    flash(f'Bienvenido, {user.nombre}! (Facebook)', 'success')
    return respuesta


@app.route('/auth/facebook/js', methods=['POST'])
def auth_facebook_js():
    # Accepts JSON: { "access_token": "<fb_token>" }
    data = request.get_json(silent=True) or {}
    fb_token = data.get('access_token')
    if not fb_token:
        return jsonify({'ok': False, 'error': 'access_token missing'}), 400

    if not app_config.FACEBOOK_CLIENT_ID or not app_config.FACEBOOK_CLIENT_SECRET:
        return jsonify({'ok': False, 'error': 'Facebook OAuth not configured on server'}), 500

    # Verify token using app access token
    app_token = f"{app_config.FACEBOOK_CLIENT_ID}|{app_config.FACEBOOK_CLIENT_SECRET}"
    try:
        dbg = requests.get('https://graph.facebook.com/debug_token', params={
            'input_token': fb_token,
            'access_token': app_token
        }, timeout=8)
        dbg.raise_for_status()
        dbgj = dbg.json()
    except Exception as e:
        logging.exception('Error verifying FB token')
        return jsonify({'ok': False, 'error': 'token_verification_failed'}), 400

    data_dbg = dbgj.get('data') or {}
    if not data_dbg.get('is_valid'):
        return jsonify({'ok': False, 'error': 'invalid_token'}), 400

    fb_user_id = data_dbg.get('user_id')
    if not fb_user_id:
        return jsonify({'ok': False, 'error': 'no_user_id'}), 400

    # Fetch profile using the user's token
    try:
        prof = requests.get(f'https://graph.facebook.com/{fb_user_id}', params={
            'fields': 'id,name,email,picture',
            'access_token': fb_token
        }, timeout=8)
        prof.raise_for_status()
        userinfo = prof.json()
    except Exception:
        logging.exception('Error fetching FB profile')
        return jsonify({'ok': False, 'error': 'profile_fetch_failed'}), 400

    email = userinfo.get('email')
    nombre = userinfo.get('name') or (email.split('@')[0] if email else f'fb_{fb_user_id}')
    if not email:
        return jsonify({'ok': False, 'error': 'email_not_provided'}), 400

    # Create or get user
    from QUERYS.queryLogin import get_usuario
    from QUERYS.querysRegistro import create_user
    from MODELS.Usuario import Usuario

    user = get_usuario(email)
    if not user:
        random_pw = secrets.token_urlsafe(16)
        nuevo = Usuario(nombre=nombre, email=email, password=random_pw)
        created = create_user(nuevo)
        if not created:
            return jsonify({'ok': False, 'error': 'user_creation_failed'}), 500
        user = get_usuario(email)

    # Set session and JWT cookies (same as callback)
    try:
        from RUTAS.login_ruta import get_rol_name
        nombre_rol = get_rol_name(user.rol_id)
    except Exception:
        nombre_rol = None

    session.permanent = True
    session['logged'] = True
    session['user_id'] = user.id
    session['user_name'] = user.nombre
    session['tema'] = 1 if user.tema == b'\x01' else 0
    session['rol_id'] = str(user.rol_id)
    session['rol_name'] = nombre_rol

    access_token = crear_access_token(user.id)
    refresh_token = crear_refresh_token(user.id)

    respuesta = make_response(jsonify({'ok': True, 'redirect': url_for('dashboard')}))
    respuesta.set_cookie('access_token', access_token, max_age=2592000, httponly=True, samesite='Lax')
    respuesta.set_cookie('refresh_token', refresh_token, max_age=2592000, httponly=True, samesite='Lax')
    return respuesta


@app.route('/logout')
@eliminar_token
def logout():
    session.clear()
    session.permanent = False
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
@limiter.limit("50 per hour")          # Limita peticiones a 50/hora
@login_required                        # Solo usuarios logueados
@lideres_required                       # Solo líderes o admin
@verificar_y_renovar_token             # Valida y renueva JWT
def crear_grupo():
    return crear_grupo_rutas()          # Llama a la función que maneja la lógica


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


@app.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
@login_required
@lideres_required
@verificar_y_renovar_token
def gestionar_puntos(grupo_id):
    return gestionar_puntos_ruta(grupo_id)
    

@app.route('/admin/medallas', methods=['GET', 'POST'])
@admin_required
@verificar_y_renovar_token
def gestionar_medallas():
    return gestionar_medallas_ruta(app)

@app.route('/perfil')
@login_required
@verificar_y_renovar_token
def perfil():
    return perfil_ruta()

@app.route('/ranking')
@login_required
def ranking_global():
    return ranking_global_rutas()

@app.route('/subir_imagen_medalla', methods=['POST'])
@limiter.limit("100 per hour")
@verificar_y_renovar_token
def subir_imagen_medalla():
    return subir_imagen_medalla_ruta(app)

@app.route('/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
@lideres_required
def tomar_asistencia(grupo_id):
    return tomar_asistencia_ruta(grupo_id)

#=============================================================================#
# Admin 
#=============================================================================#

@app.route('/admin')
@login_required
@admin_required
@limiter.limit("1000 per hour")
def admin():
    return admin_ruta()

@app.route('/editar_rol', methods=['POST'])
@login_required
@admin_required
def rol():
    return editar_rol()

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    return refresh_ruta()

if __name__ == '__main__':
    # Ejecutar aplicación
    app.run()
    #debug=True, host='0.0.0.0', port=5000
