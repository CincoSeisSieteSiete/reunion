from bd import *
from typing import Optional, Dict, Any, List 
import logging
"""Solo deben ir las querys aqui, no logica de negocio ni conexiones"""

def query_obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.email = %s
            """, (email,))
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error al obtener usuario por email: {e}")
        return None
    finally:
        conexion.close()
        
def query_encontrar_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error al obtener usuario por ID: {e}")
        return None
    finally:
        conexion.close()
    