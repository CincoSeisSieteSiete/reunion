from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, date
import os
import secrets
from app.rutas.decoradores import requiere_login, requiere_admin, requiere_lider
from app.logica import (
    obtener_usuario_por_email,
    verificar_contraseña,
    crear_usuario,
    obtener_usuario_por_id,
    obtener_grupos_usuario,
    obtener_todos_los_grupos,
    unirse_a_grupo,
    obtener_grupo_por_id,
    generar_codigo_invitacion,
    registrar_asistencia,
    obtener_asistencias_usuario,
    obtener_miembros_grupo,
    obtener_ranking_global,
    obtener_medallas_usuario,
    obtener_usuarios_para_admin,
    cambiar_rol_usuario,
    cambiar_contraseña_usuario,
    obtener_cumpleaños_proximos
)
from conexion import obtener_conexion


def registrar_rutas(aplicacion: Flask) -> None:
    """Registra todas las rutas de la aplicación"""

    @aplicacion.errorhandler(404)
    def pagina_no_encontrada(error):
        return render_template('404.html'), 404

    @aplicacion.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @aplicacion.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            password = request.form.get('password')
            fecha_nacimiento = request.form.get('fecha_nacimiento')
            
            exito, mensaje = crear_usuario(nombre, email, password, fecha_nacimiento)
            
            if exito:
                flash(mensaje, 'success')
                return redirect(url_for('login'))
            else:
                flash(mensaje, 'danger')
                return redirect(url_for('registro'))
        
        return render_template('register.html')

    @aplicacion.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            usuario = obtener_usuario_por_email(email)
            
            if usuario and verificar_contraseña(usuario['password'], password):
                session['user_id'] = usuario['id']
                session['user_name'] = usuario['nombre']
                session['user_rol'] = usuario['rol']
                flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
        
        return render_template('login.html')

    @aplicacion.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada exitosamente', 'info')
        return redirect(url_for('login'))

    @aplicacion.route('/dashboard', methods=['GET', 'POST'])
    @requiere_login
    def dashboard():
        usuario = obtener_usuario_por_id(session['user_id'])
        
        if request.method == 'POST' and 'fecha_nacimiento' in request.form:
            nueva_fecha = request.form['fecha_nacimiento']
            conexion = obtener_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("UPDATE usuarios SET fecha_nacimiento = %s WHERE id = %s",
                                   (nueva_fecha, session['user_id']))
                    conexion.commit()
                usuario = obtener_usuario_por_id(session['user_id'])
                flash('Fecha de nacimiento actualizada', 'success')
            finally:
                conexion.close()
        
        grupos = obtener_grupos_usuario(session['user_id'])
        medallas = obtener_medallas_usuario(session['user_id'])
        mostrar_panel_cumple = not usuario.get('fecha_nacimiento')
        
        return render_template('dashboard.html', user=usuario, grupos=grupos, medallas=medallas,
                               mostrar_panel_cumple=mostrar_panel_cumple)

    @aplicacion.route('/grupo/<int:grupo_id>')
    @requiere_login
    def ver_grupo(grupo_id):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as es_miembro 
                    FROM grupo_miembros 
                    WHERE grupo_id = %s AND usuario_id = %s
                """, (grupo_id, session['user_id']))
                
                if cursor.fetchone()['es_miembro'] == 0:
                    flash('No eres miembro de este grupo', 'danger')
                    return redirect(url_for('dashboard'))
        finally:
            conexion.close()
        
        grupo = obtener_grupo_por_id(grupo_id)
        miembros = obtener_miembros_grupo(grupo_id)
        es_admin = grupo['admin_id'] == session['user_id']
        
        return render_template('grupo.html', grupo=grupo, grupo_id=grupo_id, miembros=miembros, es_admin=es_admin)

    @aplicacion.route('/admin/crear-grupo', methods=['GET', 'POST'])
    @requiere_login
    @requiere_lider
    def crear_grupo():
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            
            if not nombre:
                flash('El nombre del grupo es obligatorio', 'danger')
                return redirect(url_for('crear_grupo'))
            
            codigo = generar_codigo_invitacion()
            
            conexion = obtener_conexion()
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO grupos (nombre, descripcion, admin_id, codigo_invitacion) VALUES (%s, %s, %s, %s)",
                        (nombre, descripcion, session['user_id'], codigo)
                    )
                    grupo_id = cursor.lastrowid
                    
                    cursor.execute(
                        "INSERT INTO grupo_miembros (grupo_id, usuario_id) VALUES (%s, %s)",
                        (grupo_id, session['user_id'])
                    )
                    conexion.commit()
                    flash(f'Grupo creado exitosamente', 'success')
                    return redirect(url_for('ver_grupo', grupo_id=grupo_id))
            finally:
                conexion.close()
        
        return render_template('crear_grupo.html')

    @aplicacion.route('/unirse-grupo', methods=['GET', 'POST'])
    @requiere_login
    def unirse_grupo():
        if request.method == 'POST':
            codigo = request.form.get('codigo')
            exito, mensaje = unirse_a_grupo(session['user_id'], codigo)
            
            if exito:
                flash(mensaje, 'success')
                conexion = obtener_conexion()
                try:
                    with conexion.cursor() as cursor:
                        cursor.execute("SELECT id FROM grupos WHERE codigo_invitacion = %s", (codigo,))
                        grupo = cursor.fetchone()
                        return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
                finally:
                    conexion.close()
            else:
                flash(mensaje, 'danger')
                return redirect(url_for('unirse_grupo'))
        
        return render_template('unirse_grupo.html')

    @aplicacion.route('/admin/grupo/<int:grupo_id>/asistencia', methods=['GET', 'POST'])
    @requiere_login
    @requiere_lider
    def tomar_asistencia(grupo_id):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
                grupo = cursor.fetchone()
                
                if not grupo or grupo['admin_id'] != session['user_id']:
                    flash('No tienes permisos para tomar asistencia', 'danger')
                    return redirect(url_for('dashboard'))
                
                if request.method == 'POST':
                    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
                    asistentes = request.form.getlist('asistentes')
                    
                    cursor.execute("SELECT usuario_id FROM grupo_miembros WHERE grupo_id = %s", (grupo_id,))
                    todos_miembros = [m['usuario_id'] for m in cursor.fetchall()]
                    
                    for usuario_id in todos_miembros:
                        presente = str(usuario_id) in asistentes
                        registrar_asistencia(usuario_id, grupo_id, fecha, presente)
                    
                    flash('Asistencia registrada exitosamente', 'success')
                    return redirect(url_for('ver_grupo', grupo_id=grupo_id))
                
                miembros = obtener_miembros_grupo(grupo_id)
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
            conexion.close()

    @aplicacion.route('/admin/grupo/<int:grupo_id>/puntos', methods=['GET', 'POST'])
    @requiere_login
    @requiere_lider
    def gestionar_puntos(grupo_id):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
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
                    
                    conexion.commit()
                    flash('Puntos actualizados exitosamente', 'success')
                    return redirect(url_for('gestionar_puntos', grupo_id=grupo_id))
                
                miembros = obtener_miembros_grupo(grupo_id)
                return render_template('gestionar_puntos.html', grupo_id=grupo_id, miembros=miembros)
        finally:
            conexion.close()

    @aplicacion.route('/admin/medallas', methods=['GET', 'POST'])
    @requiere_admin
    def gestionar_medallas():
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
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
                    elif accion == 'asignar':
                        usuario_id = request.form.get('usuario_id')
                        medalla_id = request.form.get('medalla_id')
                        
                        cursor.execute(
                            "INSERT IGNORE INTO usuarios_medallas (usuario_id, medalla_id) VALUES (%s, %s)",
                            (usuario_id, medalla_id)
                        )
                    elif accion == 'eliminar':
                        medalla_id = request.form.get('medalla_id')
                        cursor.execute("DELETE FROM medallas WHERE id = %s", (medalla_id,))
                    
                    conexion.commit()
                    flash('Operación realizada exitosamente', 'success')
                    return redirect(url_for('gestionar_medallas'))
                
                cursor.execute("SELECT * FROM medallas ORDER BY fecha_creacion DESC")
                medallas = cursor.fetchall()
                
                cursor.execute("SELECT id, nombre, email FROM usuarios ORDER BY nombre")
                usuarios = cursor.fetchall()
                
                medallas_path = os.path.join(aplicacion.root_path, 'static', 'medallas')
                imagenes = []
                if os.path.exists(medallas_path):
                    imagenes = [f for f in os.listdir(medallas_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
                
                return render_template('gestionar_medallas.html', medallas=medallas, usuarios=usuarios, imagenes=imagenes)
        finally:
            conexion.close()

    @aplicacion.route('/cumples')
    def cumpleanos():
        hoy = datetime.today()
        mes_actual = hoy.month
        
        cumpleaños_proximos = obtener_cumpleaños_proximos(30)
        
        return render_template('cumpleanos.html', cumpleanos=cumpleaños_proximos, hoy=hoy)

    @aplicacion.route('/perfil')
    @requiere_login
    def perfil():
        usuario = obtener_usuario_por_id(session['user_id'])
        medallas = obtener_medallas_usuario(session['user_id'])
        asistencias = obtener_asistencias_usuario(session['user_id'])
        
        return render_template('perfil.html', user=usuario, medallas=medallas, historial=asistencias)

    @aplicacion.route('/ranking')
    @requiere_login
    def ranking_global():
        ranking = obtener_ranking_global()
        return render_template('ranking.html', ranking=ranking)

    @aplicacion.route('/admin/usuarios')
    @requiere_login
    @requiere_admin
    def admin_usuarios():
        usuarios = obtener_usuarios_para_admin()
        return render_template('usuarios.html', usuarios=usuarios)

    @aplicacion.route('/admin/usuario/<int:usuario_id>/cambiar_rol', methods=['POST'])
    @requiere_login
    @requiere_admin
    def admin_cambiar_rol(usuario_id):
        nuevo_rol_id = request.form.get('rol_id')
        exito, mensaje = cambiar_rol_usuario(usuario_id, nuevo_rol_id, session['user_id'])
        
        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
        
        return redirect(url_for('admin_usuarios'))

    @aplicacion.route('/admin/usuario/<int:usuario_id>/set_password', methods=['POST'])
    @requiere_login
    @requiere_admin
    def admin_set_password(usuario_id):
        nueva_pass = request.form.get('new_password')
        exito, mensaje = cambiar_contraseña_usuario(usuario_id, nueva_pass, session['user_id'])
        
        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
        
        return redirect(url_for('admin_usuarios'))

    @aplicacion.route('/subir_imagen_medalla', methods=['POST'])
    def subir_imagen_medalla():
        imagen = request.files.get('imagen')
        nombre_imagen = request.form.get('nombre_imagen')
        
        if not imagen or not nombre_imagen:
            return "Error: faltan datos", 400
        
        extension = os.path.splitext(imagen.filename)[1]
        nuevo_nombre = f"{nombre_imagen}{extension}"
        ruta_carpeta = os.path.join(aplicacion.static_folder, 'medallas')
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_archivo = os.path.join(ruta_carpeta, nuevo_nombre)
        imagen.save(ruta_archivo)
        
        return redirect(url_for('gestionar_medallas'))

    @aplicacion.route('/salir_grupo/<int:grupo_id>', methods=['POST'])
    @requiere_login
    def salir_grupo(grupo_id):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM grupo_miembros WHERE grupo_id = %s AND usuario_id = %s",
                    (grupo_id, session['user_id'])
                )
                conexion.commit()
            flash("Has salido del grupo", "success")
        finally:
            conexion.close()
        return redirect(url_for('dashboard'))
