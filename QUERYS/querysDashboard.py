from DB.conexion import get_connection
from datetime import datetime
import logging

def get_info_usuario(usuario_id: int) -> dict:
    """Devuelve información del usuario: total de medallas y asistencias."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Total medallas
            cursor.execute("""
                SELECT COUNT(*) AS total_medallas
                FROM usuarios_medallas
                WHERE usuario_id = %s
            """, (usuario_id,))
            total_medallas = cursor.fetchone()['total_medallas']

            # Total asistencias
            cursor.execute("""
                SELECT COUNT(*) AS total_asistencias
                FROM asistencias
                WHERE usuario_id = %s AND presente = TRUE
            """, (usuario_id,))
            total_asistencias = cursor.fetchone()['total_asistencias']

            return {
                'total_medallas': total_medallas if total_medallas else 0,
                'total_asistencias': total_asistencias if total_asistencias else 0
            }
    except Exception as e:
        logging.error(f"Error al obtener la información del usuario: {e}")
        return {'total_medallas': 0, 'total_asistencias': 0}
    finally:
        connection.close()


def update_fecha_nacimiento(usuario_id: int, nueva_fecha: datetime) -> None:
    """Actualiza la fecha de nacimiento de un usuario."""
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
        connection.rollback()
    finally:
        connection.close()


def get_grupos_usuario(usuario_id: int) -> list:
    """Devuelve todos los grupos a los que pertenece el usuario con información completa."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT g.id, g.nombre, g.descripcion, g.admin_id,
                       (SELECT COUNT(*) FROM grupo_miembros WHERE grupo_id = g.id) AS total_miembros
                FROM grupo_miembros gm
                INNER JOIN grupos g ON gm.grupo_id = g.id
                WHERE gm.usuario_id = %s
                ORDER BY g.nombre ASC
            """, (usuario_id,))
            resultado = cursor.fetchall()
            return resultado
    except Exception as e:
        logging.error(f"Error al obtener la información de grupos: {e}")
        return []
    finally:
        connection.close()


def get_medallas_usuario(usuario_id: int) -> list:
    """Devuelve todas las medallas obtenidas por un usuario."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.id, m.nombre, m.descripcion, m.imagen, um.fecha_obtencion
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (usuario_id,))
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener las medallas del usuario: {e}")
        return []
    finally:
        connection.close()


def get_cumpleanos_mes(usuario_id: int, mes: int) -> list:
    """Devuelve los cumpleaños del mes de los usuarios en los mismos grupos que el usuario."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.fecha_nacimiento, g.nombre AS grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON gm.usuario_id = u.id
                INNER JOIN grupos g ON g.id = gm.grupo_id
                WHERE gm.grupo_id IN (
                    SELECT grupo_id FROM grupo_miembros WHERE usuario_id = %s
                )
                AND MONTH(u.fecha_nacimiento) = %s
                ORDER BY DAY(u.fecha_nacimiento) ASC
            """, (usuario_id, mes))
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener los cumpleaños del mes: {e}")
        return []
    finally:
        connection.close()
