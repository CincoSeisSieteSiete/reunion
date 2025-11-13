from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os
from FUNCIONES.Decoradores import login_required, admin_required, lideres_required


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Nioy')
# Configuración de la aplicación
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Admin Apartados ==========================================================================

@app.route('/admin/usuarios')
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
    return render_template('admin/usuarios.html', usuarios=usuarios)

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




@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        fecha_nacimiento = request.form.get('fecha_nacimiento')

        if not nombre or not email or not password or not fecha_nacimiento:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('register'))
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('El email ya está registrado', 'danger')
                    return redirect(url_for('register'))
                
                # Crear usuario con rol por defecto 'usuario'
                hashed_password = generate_password_hash(password)
                # Obtenemos el id del rol 'usuario'
                cursor.execute("SELECT id FROM roles WHERE nombre = 'usuario'")
                rol = cursor.fetchone()
                rol_id = rol['id'] if rol else 2  # fallback si no existe

                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, rol_id) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, email, hashed_password, fecha_nacimiento, rol_id)
                )
                connection.commit()
                flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
                return redirect(url_for('login'))
        finally:
            connection.close()
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Traer usuario con el nombre del rol
                cursor.execute("""
                    SELECT u.*, r.nombre AS rol
                    FROM usuarios u
                    LEFT JOIN roles r ON u.rol_id = r.id
                    WHERE u.email = %s
                """, (email,))
                user = cursor.fetchone()
                
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


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Usuario
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas
                FROM usuarios u
                WHERE u.id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            # Mostrar panel si no tiene fecha de nacimiento
            mostrar_panel_cumple = not user['fecha_nacimiento']

            # Guardar fecha si viene del form
            if request.method == 'POST' and 'fecha_nacimiento' in request.form:
                nueva_fecha = request.form['fecha_nacimiento']
                cursor.execute("UPDATE usuarios SET fecha_nacimiento = %s WHERE id = %s",
                               (nueva_fecha, session['user_id']))
                connection.commit()
                user['fecha_nacimiento'] = nueva_fecha
                mostrar_panel_cumple = False

            # Grupos
            cursor.execute("""
                SELECT g.*, 
                       (SELECT COUNT(*) FROM grupo_miembros WHERE grupo_id = g.id) as total_miembros
                FROM grupos g
                INNER JOIN grupo_miembros gm ON g.id = gm.grupo_id
                WHERE gm.usuario_id = %s
                ORDER BY g.fecha_creacion DESC
            """, (session['user_id'],))
            grupos = cursor.fetchall()

            # Medallas
            cursor.execute("""
                SELECT m.* 
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (session['user_id'],))
            medallas = cursor.fetchall()

            # Cumpleaños del mes de los miembros de los grupos del usuario
            mes_actual = date.today().month
            cursor.execute("""
                SELECT u.nombre, u.fecha_nacimiento, g.nombre AS grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON gm.usuario_id = u.id
                INNER JOIN grupos g ON g.id = gm.grupo_id
                WHERE gm.grupo_id IN (
                    SELECT grupo_id FROM grupo_miembros WHERE usuario_id = %s
                )
                AND MONTH(u.fecha_nacimiento) = %s
                ORDER BY DAY(u.fecha_nacimiento) ASC
            """, (session['user_id'], mes_actual))
            cumpleanos_mes = cursor.fetchall()
            
            return render_template('dashboard.html', user=user, grupos=grupos, medallas=medallas,
                                   mostrar_panel_cumple=mostrar_panel_cumple,
                                   cumpleanos_mes=cumpleanos_mes)
    finally:
        connection.close()

@app.route('/grupo/<int:grupo_id>')
@login_required
def ver_grupo(grupo_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el usuario es miembro del grupo
            cursor.execute("""
                SELECT COUNT(*) as es_miembro 
                FROM grupo_miembros 
                WHERE grupo_id = %s AND usuario_id = %s
            """, (grupo_id, session['user_id']))
            
            if cursor.fetchone()['es_miembro'] == 0:
                flash('No eres miembro de este grupo', 'danger')
                return redirect(url_for('dashboard'))
            
            # Obtener información del grupo
            cursor.execute("""
                SELECT g.*, u.nombre as admin_nombre
                FROM grupos g
                INNER JOIN usuarios u ON g.admin_id = u.id
                WHERE g.id = %s
            """, (grupo_id,))
            grupo = cursor.fetchone()
            
            # Obtener ranking del grupo
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND grupo_id = %s AND presente = TRUE) as asistencias_grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.puntos DESC, u.racha DESC
            """, (grupo_id, grupo_id))
            ranking = cursor.fetchall()
            
            # Verificar si el usuario es admin del grupo
            es_admin = grupo['admin_id'] == session['user_id']
            
            return render_template('grupo.html', grupo=grupo, grupo_id=grupo_id, ranking=ranking, es_admin=es_admin)
    finally:
        connection.close()


@app.route('/admin/crear-grupo', methods=['GET', 'POST'])
@login_required
@lideres_required
def crear_grupo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre del grupo es obligatorio', 'danger')
            return redirect(url_for('crear_grupo'))
        
        # Generar código de invitación único
        codigo = secrets.token_urlsafe(8)
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO grupos (nombre, descripcion, admin_id, codigo_invitacion) VALUES (%s, %s, %s, %s)",
                    (nombre, descripcion, session['user_id'], codigo)
                )
                grupo_id = cursor.lastrowid
                
                # Agregar al admin como miembro del grupo
                cursor.execute(
                    "INSERT INTO grupo_miembros (grupo_id, usuario_id) VALUES (%s, %s)",
                    (grupo_id, session['user_id'])
                )
                
                connection.commit()
                flash(f'Grupo creado exitosamente. Código de invitación: {codigo}', 'success')
                return redirect(url_for('ver_grupo', grupo_id=grupo_id))
        finally:
            connection.close()
    
    return render_template('crear_grupo.html')

@app.route('/unirse-grupo', methods=['GET', 'POST'])
@login_required
def unirse_grupo():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                # Buscar grupo por código
                cursor.execute("SELECT id FROM grupos WHERE codigo_invitacion = %s", (codigo,))
                grupo = cursor.fetchone()
                
                if not grupo:
                    flash('Código de invitación inválido', 'danger')
                    return redirect(url_for('unirse_grupo'))
                
                # Verificar si ya es miembro
                cursor.execute(
                    "SELECT id FROM grupo_miembros WHERE grupo_id = %s AND usuario_id = %s",
                    (grupo['id'], session['user_id'])
                )
                
                if cursor.fetchone():
                    flash('Ya eres miembro de este grupo', 'info')
                    return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
                
                # Agregar como miembro
                cursor.execute(
                    "INSERT INTO grupo_miembros (grupo_id, usuario_id) VALUES (%s, %s)",
                    (grupo['id'], session['user_id'])
                )
                
                # Registrar uso de invitación
                cursor.execute(
                    "INSERT INTO invitaciones (codigo, grupo_id, usado_por, fecha_uso) VALUES (%s, %s, %s, NOW())",
                    (codigo, grupo['id'], session['user_id'])
                )
                
                connection.commit()
                flash('Te has unido al grupo exitosamente', 'success')
                return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
        finally:
            connection.close()
    
    return render_template('unirse_grupo.html')

@app.route('/admin/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
@login_required
@lideres_required
def tomar_asistencia(grupo_id):
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el usuario es admin del grupo
            cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
            grupo = cursor.fetchone()
            
            if not grupo or grupo['admin_id'] != session['user_id']:
                flash('No tienes permisos para tomar asistencia en este grupo', 'danger')
                return redirect(url_for('dashboard'))
            
            if request.method == 'POST':
                fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
                asistentes = request.form.getlist('asistentes')
                
                # Obtener todos los miembros del grupo
                cursor.execute("""
                    SELECT usuario_id FROM grupo_miembros WHERE grupo_id = %s
                """, (grupo_id,))
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
            
            # GET: Mostrar formulario
            cursor.execute("""
                SELECT u.id, u.nombre, u.racha, u.puntos
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            miembros = cursor.fetchall()
            
            # Obtener asistencia de hoy si existe
            hoy = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT usuario_id FROM asistencias 
                WHERE grupo_id = %s AND fecha = %s AND presente = TRUE
            """, (grupo_id, hoy))
            asistentes_hoy = [a['usuario_id'] for a in cursor.fetchall()]
            
            return render_template('tomar_asistencia.html', 
                                 grupo_id=grupo_id, 
                                 miembros=miembros, 
                                 asistentes_hoy=asistentes_hoy,
                                 fecha_hoy=hoy)
    finally:
        connection.close()

def actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha_actual):
    """Actualiza la racha y puntos del usuario"""
    # Obtener última asistencia
    cursor.execute("""
        SELECT fecha FROM asistencias 
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (usuario_id, grupo_id, fecha_actual))
    
    ultima_asistencia = cursor.fetchone()
    
    # Calcular racha
    fecha_obj = datetime.strptime(fecha_actual, '%Y-%m-%d').date()
    
    if ultima_asistencia:
        ultima_fecha = ultima_asistencia['fecha']
        diferencia = (fecha_obj - ultima_fecha).days
        
        if diferencia <= 7:  # Asistencia dentro de la semana
            cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
        else:  # Se rompió la racha
            cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
    else:
        # Primera asistencia
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

@app.route('/cumples')
def cumpleanos():
    hoy = datetime.today()
    mes_actual = hoy.month
    dia_actual = hoy.day

    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Usuarios que cumplen años este mes
            cursor.execute("""
                SELECT nombre, fecha_nacimiento
                FROM usuarios
                WHERE MONTH(fecha_nacimiento) = %s
                ORDER BY DAY(fecha_nacimiento)
            """, (mes_actual,))
            cumple_mes = cursor.fetchall()

            # Usuarios que cumplen hoy
            cursor.execute("""
                SELECT nombre
                FROM usuarios
                WHERE MONTH(fecha_nacimiento) = %s AND DAY(fecha_nacimiento) = %s
            """, (mes_actual, dia_actual))
            cumple_hoy = cursor.fetchall()
    finally:
        connection.close()

    return render_template('cumpleanos.html', cumple_mes=cumple_mes, cumple_hoy=cumple_hoy, hoy=hoy)


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


if __name__ == '__main__':
    # Inicializar base de datos
    db.init_db()
    
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
