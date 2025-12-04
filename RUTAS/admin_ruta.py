from flask import Blueprint, render_template, request, redirect, flash
from DB.conexion import get_connection
import logging

# =========================
# FUNCIONES DE DATOS
# =========================
def get_lideres_count():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol_id = (SELECT id FROM roles WHERE nombre='lider')")
            resultado = cursor.fetchone()
            if resultado and 'COUNT(*)' in resultado:
                return resultado['COUNT(*)']
            elif resultado and isinstance(resultado, tuple):
                return resultado[0]
            return 0
    except Exception as e:
        logging.error(f"Error al contar líderes: {e}")
        return 0
    finally:
        if connection:
            connection.close()

def get_user_count():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            resultado = cursor.fetchone()
            if resultado and 'COUNT(*)' in resultado:
                return resultado['COUNT(*)']
            elif resultado and isinstance(resultado, tuple):
                return resultado[0]
            return 0
    except Exception as e:
        logging.error(f"Error al contar usuarios: {e}")
        return 0
    finally:
        if connection:
            connection.close()

def get_group_count():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM grupos;")
            resultado = cursor.fetchone()
            if resultado and 'COUNT(*)' in resultado:
                return resultado['COUNT(*)']
            elif resultado and isinstance(resultado, tuple):
                return resultado[0]
            return 0
    except Exception as e:
        logging.error(f"Error al contar grupos: {e}")
        return 0
    finally:
        if connection:
            connection.close()

def get_all_users():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.email, u.rol_id, r.nombre AS rol_nombre
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                ORDER BY u.nombre;
            """)
            usuarios = cursor.fetchall()
            return usuarios if usuarios else []
    except Exception as e:
        logging.error(f"Error al obtener usuarios: {e}")
        return []
    finally:
        if connection:
            connection.close()

def get_all_roles():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM roles ORDER BY nombre;")
            roles = cursor.fetchall()
            return roles if roles else []
    except Exception as e:
        logging.error(f"Error al obtener roles: {e}")
        return []
    finally:
        if connection:
            connection.close()

# =========================
# RUTAS
# =========================
def admin_ruta():
    data = get_user_count()
    group_count = get_group_count()
    lideres_count = get_lideres_count()
    usuarios = get_all_users()
    roles = get_all_roles()
    return render_template("admin/admin.html",
                           data=data,
                           group_count=group_count,
                           lideres_count=lideres_count,
                           usuarios=usuarios,
                           roles=roles)

