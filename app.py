from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import db
import secrets
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Nioy')

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir rol de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))
        
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT rol FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user or user['rol'] != 'admin':
                    flash('No tienes permisos de administrador', 'danger')
                    return redirect(url_for('index'))
        finally:
            connection.close()
        
        return f(*args, **kwargs)
    return decorated_function

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
        
        if not nombre or not email or not password:
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
                
                # Crear usuario
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                    (nombre, email, hashed_password)
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
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['user_name'] = user['nombre']
                    session['user_rol'] = user['rol']
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

@app.route('/dashboard')
@login_required
def dashboard():
    connection = db.get_connection()
    try:
        with connection.cursor() as cursor:
            # Obtener información del usuario
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas
                FROM usuarios u
                WHERE u.id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            # Obtener grupos del usuario
            cursor.execute("""
                SELECT g.*, 
                       (SELECT COUNT(*) FROM grupo_miembros WHERE grupo_id = g.id) as total_miembros
                FROM grupos g
                INNER JOIN grupo_miembros gm ON g.id = gm.grupo_id
                WHERE gm.usuario_id = %s
                ORDER BY g.fecha_creacion DESC
            """, (session['user_id'],))
            grupos = cursor.fetchall()
            
            # Obtener medallas del usuario
            cursor.execute("""
                SELECT m.* 
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (session['user_id'],))
            medallas = cursor.fetchall()
            
            return render_template('dashboard.html', user=user, grupos=grupos, medallas=medallas)
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
            
            return render_template('grupo.html', grupo=grupo, ranking=ranking, es_admin=es_admin)
    finally:
        connection.close()

@app.route('/admin/crear-grupo', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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
@admin_required
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
            
            return render_template('gestionar_medallas.html', medallas=medallas, usuarios=usuarios)
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

if __name__ == '__main__':
    # Inicializar base de datos
    db.init_db()
    
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
