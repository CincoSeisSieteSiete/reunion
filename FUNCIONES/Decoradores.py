from functools import wraps
from flask import session, redirect, url_for, flash
from DB.conexion import get_connection

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

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if not user:
                    flash('No tienes permisos de líder', 'danger')
                    return redirect(url_for('index'))

                cursor.execute("SELECT nombre FROM roles WHERE rol_id = %s", (user['rol_id'],))
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

        connection = get_connection()
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

def grupo_admin_required(f):
    """
    Verifica que el usuario sea admin del grupo específico o tenga rol de admin global.
    La función decorada DEBE tener un parámetro 'grupo_id'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión', 'warning')
            return redirect(url_for('login'))

        # Obtener grupo_id de los kwargs
        grupo_id = kwargs.get('grupo_id')
        if not grupo_id:
            flash('Grupo no especificado', 'error')
            return redirect(url_for('dashboard'))

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Verificar si es admin global
                cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                    rol = cursor.fetchone()
                    if rol and rol['nombre'] == 'admin':
                        # Es admin global, tiene acceso
                        return f(*args, **kwargs)
                
                # Verificar si es admin del grupo específico
                cursor.execute("""
                    SELECT admin_id FROM grupos WHERE id = %s
                """, (grupo_id,))
                grupo = cursor.fetchone()
                
                if not grupo:
                    flash('Grupo no encontrado', 'error')
                    return redirect(url_for('dashboard'))
                
                # DEBUG: Ver por qué falla la comparación
                print(f"DEBUG PERMISOS:")
                print(f"  Usuario en sesión: {session['user_id']} (Tipo: {type(session['user_id'])})")
                print(f"  Admin del grupo: {grupo['admin_id']} (Tipo: {type(grupo['admin_id'])})")
                
                # Convertir ambos a string para asegurar comparación correcta
                if str(grupo['admin_id']) == str(session['user_id']):
                    # Es admin del grupo
                    return f(*args, **kwargs)
                
                # No tiene permisos
                flash('No tienes permisos para gestionar este grupo', 'error')
                return redirect(url_for('ver_grupo', grupo_id=grupo_id))
                
        finally:
            connection.close()
    
    return decorated_function
