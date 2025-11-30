from functools import wraps
from flask import session, redirect, url_for, flash
from DB.conexion import get_connection

# =========================
# LOGIN REQUERIDO
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# LÍDER O ADMIN REQUERIDO
# =========================
def lideres_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol_name') not in ['lider', 'admin']:
            flash("No tienes permiso para acceder a esta página", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# ADMIN REQUERIDO
# =========================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol_name') != 'admin':
            flash('No tienes permisos de administrador', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# ADMIN DE GRUPO REQUERIDO
# =========================
def grupo_admin_required(f):
    """
    Verifica que el usuario sea admin del grupo específico o admin global.
    La función decorada debe tener un parámetro 'grupo_id'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))

        grupo_id = kwargs.get('grupo_id')
        if not grupo_id:
            flash('Grupo no especificado', 'error')
            return redirect(url_for('dashboard'))

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Admin global
                cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                    rol = cursor.fetchone()
                    if rol and rol['nombre'] == 'admin':
                        return f(*args, **kwargs)

                # Admin del grupo específico
                cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
                grupo = cursor.fetchone()
                if grupo and str(grupo['admin_id']) == str(session['user_id']):
                    return f(*args, **kwargs)

                flash('No tienes permisos para gestionar este grupo', 'error')
                return redirect(url_for('ver_grupo', grupo_id=grupo_id))

        finally:
            connection.close()

    return decorated_function
