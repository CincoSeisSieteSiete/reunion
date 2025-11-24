from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import os
from FUNCIONES.Decoradores import login_required, admin_required, lideres_required

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

app = Flask(__name__)

app.register_blueprint(configuraciones_usuarios_rutas)

app.secret_key = os.getenv('SECRET_KEY', 'Nioy')
app.permanent_session_lifetime = timedelta(days=10)
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30


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
def register():
    return register_rutas()

@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_rutas()

@app.route('/logout')
def logout():
    session.clear()
    session.permanent = False
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not session.get("logged"):
        return redirect("/login")
    return dashboard_rutas(request)

@app.route('/grupo/<int:grupo_id>')
@login_required
def ver_grupo(grupo_id):
    return ver_grupo_ruta(grupo_id)

@app.route('/crear_grupo', methods=['GET', 'POST'])
@login_required
@lideres_required
def crear_grupo():
    return crear_grupo_rutas()

@app.route('/unirse_grupo', methods=['GET', 'POST'])
@login_required
def unirse_grupo():
    return unirse_grupo_rutas()

@app.route('/cumples/<int:id_grupo>')
@login_required
def cumpleanos(id_grupo):
    return cumpleanos_rutas(id_grupo)



@app.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
@login_required
@lideres_required
def gestionar_puntos(grupo_id):
    return gestionar_puntos_ruta(grupo_id)
    



@app.route('/admin/medallas', methods=['GET', 'POST'])
@admin_required
def gestionar_medallas():
    return gestionar_medallas_ruta(app)

@app.route('/perfil')
@login_required
def perfil():
    return perfil_ruta()


@app.route('/ranking')
@login_required
def ranking_global():
    return ranking_global_rutas()

@app.route('/subir_imagen_medalla', methods=['POST'])
def subir_imagen_medalla():
    return subir_imagen_medalla_ruta(app)

@app.route('/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
@lideres_required
def tomar_asistencia(grupo_id):
    return tomar_asistencia_ruta(grupo_id)


if __name__ == '__main__':
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
    #debug=True, host='0.0.0.0', port=5000
