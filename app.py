from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter, util
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime, timedelta
import os
from FUNCIONES.Decoradores import login_required, admin_required, lideres_required, grupo_admin_required

# IMPORTAR RUTAS
from RUTAS.dashboard_ruta import dashboard_rutas
from RUTAS.grupo_ruta import ver_grupo_ruta
from RUTAS.register_ruta import register_rutas
from RUTAS.login_ruta import login_rutas
from RUTAS.crear_grupo_ruta import crear_grupo_rutas
from RUTAS.unirse_grupo_ruta import unirse_grupo_rutas
from RUTAS.cumpleanos_ruta import cumpleanos_rutas
from RUTAS.ranking_ruta import ranking_global_rutas
from RUTAS.configuraciones_usuarios_rutas import configuracion, configuraciones_usuarios_rutas
from RUTAS.tema_ruta import cambiar_tema
from RUTAS.ajustar_puntos_ruta import gestionar_puntos_ruta
from RUTAS.gestionar_medallas_ruta import gestionar_medallas_ruta
from RUTAS.perfil_ruta import perfil_ruta
from RUTAS.asistencia_ruta import tomar_asistencia_ruta
from RUTAS.subir_imagen_ruta import subir_imagen_medalla_ruta
from RUTAS.JWT_ruta import refresh_ruta

from JWT.JWT import verificar_y_renovar_token, eliminar_token, crear_access_token
from flask_jwt_extended import  JWTManager, jwt_required
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
app.config['JWT_COOKIE_CSRF_PROTECT'] = False    # Protección CSRF
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Previene CSRF
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
jwt = JWTManager(app)

logging.basicConfig(level=logging.INFO)

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



@app.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
@login_required
<<<<<<< Updated upstream
@lideres_required
@verificar_y_renovar_token
=======
@grupo_admin_required
>>>>>>> Stashed changes
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
@limiter.limit("3 per hour")
@verificar_y_renovar_token
def subir_imagen_medalla():
    return subir_imagen_medalla_ruta(app)

@app.route('/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
<<<<<<< Updated upstream
@lideres_required
@limiter.limit("2 per day")
@verificar_y_renovar_token
=======
@grupo_admin_required
>>>>>>> Stashed changes
def tomar_asistencia(grupo_id):
    return tomar_asistencia_ruta(grupo_id)


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    return refresh_ruta()



if __name__ == '__main__':
    # Ejecutar aplicación
    app.run(debug=True, host='127.0.0.1', port=5000)
    #debug=True, host='0.0.0.0', port=5000
