from DB.conexion import get_connection
from MODELS.Grupo import Grupo, GrupoMiembro
from datetime import datetime
import logging

def get_info_usuario(usuario_id) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total_medallas
                FROM usuarios_medallas
                WHERE usuario_id = %s
            """, (usuario_id,))
            resultado = cursor.fetchone()
            return resultado
    except Exception as e:
        logging.error(f"Error al obtener la cantidad de medallas: {e}")
        return None
    finally:
        connection.close()
        
def update_fecha_nacimiento(usuario_id: int, nueva_fecha: datetime) -> None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios
                SET fecha_nacimiento = %s
                WHERE id = %s
            """, (nueva_fecha, usuario_id))
            connection.commit()
    except Exception as e:
        logging.error(f"Error al actualizar la fecha de nacimiento: {e}")
    finally:
        connection.close()
        
def get_grupos_usuario(usuario_id : int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT gm.*, g.nombre AS nombre_grupo
                FROM grupo_miembros gm
                INNER JOIN grupos g ON gm.grupo_id = g.id
                WHERE gm.usuario_id = %s
            """, (usuario_id,))
            resultado = cursor.fetchall()
            return resultado
    except Exception as e:
        logging.error(f"Error al obtener la información de grupo_miembros: {e}")
        return []
    finally:
        connection.close()
        
        
def get_medallas_usuario(usuario_id: int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (usuario_id,))
            resultado = cursor.fetchall()
            return resultado
    except Exception as e:
        logging.error(f"Error al obtener las medallas del usuario: {e}")
        return []
    finally:
        connection.close()
        
        
def get_cumpleanos_mes(usuario_id: int, mes: int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
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
            """, (usuario_id, mes))
            resultado = cursor.fetchall()
            return resultado
    except Exception as e:
        logging.error(f"Error al obtener los cumpleaños del mes: {e}")
        return []
    finally:
        connection.close()