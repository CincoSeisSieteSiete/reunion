from functools import wraps
from flask import session, redirect, url_for, flash
import db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def lideres_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))

        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user:
                    flash('No tienes permisos de líder', 'danger')
                    return redirect(url_for('index'))

                cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                rol = cursor.fetchone()
                if not rol or rol['nombre'] not in ['admin', 'lider']:
                    flash('No tienes permisos de líder', 'danger')
                    return redirect(url_for('index'))
        finally:
            connection.close()
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))

        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user:
                    flash('No tienes permisos de administrador', 'danger')
                    return redirect(url_for('index'))

                cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                rol = cursor.fetchone()
                if not rol or rol['nombre'] != 'admin':
                    flash('No tienes permisos de administrador', 'danger')
                    return redirect(url_for('index'))
        finally:
            connection.close()
        
        return f(*args, **kwargs)
    return decorated_function
