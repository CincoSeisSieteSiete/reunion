from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
import db
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


app = Flask(__name__)
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



@app.route('/usuarios')
@login_required
@admin_required
def admin_usuarios():
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.email, u.puntos, u.racha, u.fecha_nacimiento,
                       u.fecha_registro, u.rol_id, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                ORDER BY u.id DESC
            """)
            usuarios = cursor.fetchall()
    finally:
        conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/<int:usuario_id>/cambiar_rol', methods=['POST'])
@login_required
@admin_required
def admin_cambiar_rol(usuario_id):
    nuevo_rol_id = request.form.get('rol_id')
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar que el rol existe
            cursor.execute("SELECT nombre FROM roles WHERE id = %s", (nuevo_rol_id,))
            rol = cursor.fetchone()
            if not rol:
                flash('Rol inválido', 'danger')
                return redirect(url_for('admin_usuarios'))

            # Actualizar rol del usuario
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE id = %s", (nuevo_rol_id, usuario_id))

            # Registrar acción en admin_logs
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle)
                VALUES (%s, %s, %s, %s)
            """, (session['user_id'], 'cambiar_rol', usuario_id, f'nuevo_rol={rol["nombre"]}'))

            conn.commit()
            flash(f'Rol actualizado a {rol["nombre"]}', 'success')
    finally:
        conn.close()
    return redirect(url_for('admin_usuarios'))


@app.route('/admin/usuario/<int:usuario_id>/set_password', methods=['POST'])
@login_required
@admin_required
def admin_set_password(usuario_id):
    nueva_pass = request.form.get('new_password')
    if not nueva_pass or len(nueva_pass) < 6:
        flash('Contraseña inválida (mínimo 6 caracteres)', 'danger')
        return redirect(url_for('admin_usuarios'))

    hashed = generate_password_hash(nueva_pass)
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (hashed, usuario_id))
            cursor.execute("INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle) VALUES (%s, %s, %s, %s)",
                           (session['user_id'], 'set_password', usuario_id, 'admin_set_password'))
            conn.commit()
        flash('Contraseña actualizada correctamente (temporal)', 'success')
    finally:
        conn.close()
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuario/<int:usuario_id>/reset_token', methods=['POST'])
@login_required
@admin_required
def admin_reset_token(usuario_id):
    token = secrets.token_urlsafe(32)
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET reset_token = %s, reset_expires = DATE_ADD(NOW(), INTERVAL 1 HOUR) WHERE id = %s",
                           (token, usuario_id))
            cursor.execute("INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle) VALUES (%s, %s, %s, %s)",
                           (session['user_id'], 'generar_reset_token', usuario_id, f'token={token}'))
            conn.commit()
        # Aquí debes enviar el email con el token — ejemplo: /reset_password/<token>
        flash('Token de recuperación generado. Envía el enlace al usuario.', 'info')
    finally:
        conn.close()
    return redirect(url_for('admin_usuarios'))


# ==========================================================================================


def actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha_actual):
    """Actualiza la racha y puntos del usuario"""
    if isinstance(fecha_actual, datetime):
        fecha_obj = fecha_actual.date()
    else:
        fecha_obj = datetime.strptime(fecha_actual, '%Y-%m-%d').date()

    # Obtener última asistencia antes de la fecha actual
    cursor.execute("""
        SELECT fecha FROM asistencias
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (usuario_id, grupo_id, fecha_obj))
    ultima_asistencia = cursor.fetchone()

    if ultima_asistencia:
        ultima_fecha = ultima_asistencia['fecha']
        if isinstance(ultima_fecha, datetime):
            ultima_fecha = ultima_fecha.date()
        diferencia = (fecha_obj - ultima_fecha).days

        if diferencia <= 7:
            cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
        else:
            cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
    else:
        cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))


@app.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
@login_required
@lideres_required
def gestionar_puntos(grupo_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar permisos
            cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
            grupo = cursor.fetchone()
            
            if not grupo or grupo['admin_id'] != session['user_id']:
                flash('No tienes permisos', 'danger')
                return redirect(url_for('dashboard'))
            
            if request.method == 'POST':
                usuario_id = request.form.get('usuario_id')
                puntos = int(request.form.get('puntos', 0))
                accion = request.form.get('accion')
                
                if accion == 'agregar':
                    cursor.execute("UPDATE usuarios SET puntos = puntos + %s WHERE id = %s", (puntos, usuario_id))
                elif accion == 'quitar':
                    cursor.execute("UPDATE usuarios SET puntos = GREATEST(0, puntos - %s) WHERE id = %s", (puntos, usuario_id))
                
                connection.commit()
                flash('Puntos actualizados exitosamente', 'success')
                return redirect(url_for('gestionar_puntos', grupo_id=grupo_id))
            
            # Obtener miembros del grupo
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            miembros = cursor.fetchall()
            
            return render_template('gestionar_puntos.html', grupo_id=grupo_id, miembros=miembros)
    finally:
        connection.close()

@app.route('/salir_reunion/<int:reunion_id>', methods=['POST'])
@login_required
def salir_reunion(reunion_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Elimina al usuario de la reunión
            cursor.execute("""
                DELETE FROM reunion_miembros
                WHERE reunion_id = %s AND usuario_id = %s
            """, (reunion_id, session['user_id']))
            connection.commit()
        flash("Has salido de la reunión", "success")
        return redirect(url_for('dashboard'))
    finally:
        connection.close()


@app.route('/admin/medallas', methods=['GET', 'POST'])
@admin_required
def gestionar_medallas():
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                accion = request.form.get('accion')
                
                if accion == 'crear':
                    nombre = request.form.get('nombre')
                    descripcion = request.form.get('descripcion')
                    imagen = request.form.get('imagen')
                    
                    cursor.execute(
                        "INSERT INTO medallas (nombre, descripcion, imagen) VALUES (%s, %s, %s)",
                        (nombre, descripcion, imagen)
                    )
                    connection.commit()
                    flash('Medalla creada exitosamente', 'success')
                
                elif accion == 'asignar':
                    usuario_id = request.form.get('usuario_id')
                    medalla_id = request.form.get('medalla_id')
                    
                    cursor.execute(
                        "INSERT IGNORE INTO usuarios_medallas (usuario_id, medalla_id) VALUES (%s, %s)",
                        (usuario_id, medalla_id)
                    )
                    connection.commit()
                    flash('Medalla asignada exitosamente', 'success')
                
                elif accion == 'eliminar':
                    medalla_id = request.form.get('medalla_id')
                    cursor.execute("DELETE FROM medallas WHERE id = %s", (medalla_id,))
                    connection.commit()
                    flash('Medalla eliminada exitosamente', 'success')
                
                return redirect(url_for('gestionar_medallas'))
            
            # Obtener todas las medallas
            cursor.execute("SELECT * FROM medallas ORDER BY fecha_creacion DESC")
            medallas = cursor.fetchall()
            
            # Obtener todos los usuarios
            cursor.execute("SELECT id, nombre, email FROM usuarios ORDER BY nombre")
            usuarios = cursor.fetchall()

            # 🖼️ Obtener imágenes del directorio static/medallas
            medallas_path = os.path.join(app.root_path, 'static', 'medallas')
            imagenes = [f for f in os.listdir(medallas_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
            
            return render_template(
                'gestionar_medallas.html',
                medallas=medallas,
                usuarios=usuarios,
                imagenes=imagenes
            )
    finally:
        connection.close()

@app.route('/perfil')
@login_required
def perfil():
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Información del usuario
            cursor.execute("""
                SELECT u.*,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND presente = TRUE) as total_asistencias
                FROM usuarios u
                WHERE u.id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            # Medallas del usuario
            cursor.execute("""
                SELECT m.*, um.fecha_obtencion
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (session['user_id'],))
            medallas = cursor.fetchall()
            
            # Historial de asistencias
            cursor.execute("""
                SELECT a.fecha, g.nombre as grupo_nombre, a.presente
                FROM asistencias a
                INNER JOIN grupos g ON a.grupo_id = g.id
                WHERE a.usuario_id = %s
                ORDER BY a.fecha DESC
                LIMIT 20
            """, (session['user_id'],))
            historial = cursor.fetchall()
            
            return render_template('perfil.html', user=user, medallas=medallas, historial=historial)
    finally:
        connection.close()

@app.route('/ranking')
@login_required
def ranking_global():
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND presente = TRUE) as total_asistencias
                FROM usuarios u
                ORDER BY u.puntos DESC, u.racha DESC
                LIMIT 50
            """)
            ranking = cursor.fetchall()
            
            return render_template('ranking.html', ranking=ranking)
    finally:
        connection.close()

@app.route('/subir_imagen_medalla', methods=['POST'])
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
    return redirect(url_for('gestionar_medallas'))

@app.route('/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
@lideres_required
def tomar_asistencia(grupo_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
                asistentes = request.form.getlist('asistentes')  # Lista de user_id presentes

                # Obtener todos los miembros del grupo
                # un json para retornar solo los usarios id, nombres, recha y puntos
                cursor.execute("SELECT usuario_id FROM grupo_miembros WHERE grupo_id = %s", (grupo_id,))
                todos_miembros = [m['usuario_id'] for m in cursor.fetchall()]

                for usuario_id in todos_miembros:
                    presente = str(usuario_id) in asistentes

                    # Insertar o actualizar asistencia
                    cursor.execute("""
                        INSERT INTO asistencias (usuario_id, grupo_id, fecha, presente)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE presente = %s
                    """, (usuario_id, grupo_id, fecha, presente, presente))

                    if presente:
                        # Actualizar racha y puntos
                        actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha)

                connection.commit()
                flash('Asistencia registrada exitosamente', 'success')
                return redirect(url_for('ver_grupo', grupo_id=grupo_id))

            # GET: mostrar formulario de asistencia
            # muestra datos de racha y puntos actuales
            cursor.execute("""
                SELECT u.id, u.nombre, u.racha, u.puntos
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            miembros = cursor.fetchall()

            # Obtener asistencia de hoy si existe
            # para saber si el usario ya marcó presente
            hoy = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT usuario_id FROM asistencias 
                WHERE grupo_id = %s AND fecha = %s AND presente = TRUE
            """, (grupo_id, hoy))
            asistentes_hoy = [a['usuario_id'] for a in cursor.fetchall()]

            return render_template(
                'tomar_asistencia.html',
                grupo_id=grupo_id,
                miembros=miembros,
                asistentes_hoy=asistentes_hoy,
                fecha_hoy=hoy
            )
    finally:
        connection.close()


def actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha_actual):
    """
    Actualiza racha y puntos del usuario según última asistencia.
    - +10 puntos por asistencia
    - Racha aumenta si no se rompe la semana
    """
    # Convertir fecha_actual a objeto date
    fecha_obj = datetime.strptime(fecha_actual, '%Y-%m-%d').date()

    # Obtener última asistencia antes de fecha_actual
    cursor.execute("""
        SELECT fecha FROM asistencias
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (usuario_id, grupo_id, fecha_actual))
    ultima_asistencia = cursor.fetchone()

    if ultima_asistencia:
        ultima_fecha = ultima_asistencia['fecha']
        if isinstance(ultima_fecha, str):
            ultima_fecha = datetime.strptime(ultima_fecha, '%Y-%m-%d').date()
        diferencia = (fecha_obj - ultima_fecha).days

        if diferencia <= 7:  # No se rompe la racha
            cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
        else:  # Se rompe la racha
            cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
    else:
        # Primera asistencia
        cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))



if __name__ == '__main__':
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
    #debug=True, host='0.0.0.0', port=5000
