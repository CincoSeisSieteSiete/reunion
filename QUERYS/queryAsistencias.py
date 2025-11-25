from DB.conexion import get_connection
import logging
from datetime import datetime


def get_asistencia_usuario(usuario_id: int) -> list:
    """Devuelve la lista de asistencias del usuario ordenada por fecha descendente."""
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM asistencias
                WHERE usuario_id = %s
                ORDER BY fecha DESC
                """,
                (usuario_id,)
            )
            asistencias_data = cursor.fetchall()
            # Convertir cada fila a dict (DictCursor ya lo hace, pero garantizamos)
            asistencias = [dict(row) for row in asistencias_data]
            return asistencias
    except Exception as e:
        logging.error(f"Error al obtener asistencias del usuario {usuario_id}: {e}")
        return []
    finally:
        conexion.close()


def get_asistencia_por_fecha(usuario_id: int, grupo_id: int, fecha: str):
    """Obtiene la asistencia de un usuario en un grupo para una fecha concreta.
    `fecha` debe estar en formato 'YYYY-MM-DD' (solo fecha) o con hora si se necesita.
    Retorna el registro o ``None`` si no existe.
    """
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, usuario_id, grupo_id, fecha, presente
                FROM asistencias
                WHERE usuario_id = %s AND grupo_id = %s AND fecha = %s
                """,
                (usuario_id, grupo_id, fecha)
            )
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error al obtener asistencia por fecha para usuario {usuario_id}, grupo {grupo_id}: {e}")
        return None
    finally:
        conexion.close()


def insertar_asistencia(usuario_id: int, grupo_id: int, presente: bool, fecha: str = None) -> None:
    """Inserta o actualiza la asistencia de un usuario.
    Si ``fecha`` es ``None`` se usa la fecha actual (solo día).
    ``presente`` indica si el usuario asistió (True/False).
    """
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            if fecha is None:
                fecha = datetime.now().strftime('%Y-%m-%d')
            # ``presente`` se guarda como entero 1/0 para compatibilidad con MySQL
            presente_val = int(presente)
            cursor.execute(
                """
                INSERT INTO asistencias (usuario_id, grupo_id, fecha, presente)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE presente = %s
                """,
                (usuario_id, grupo_id, fecha, presente_val, presente_val)
            )
            conexion.commit()
    except Exception as e:
        logging.error(f"Error al insertar asistencia para usuario {usuario_id}, grupo {grupo_id}: {e}")
        conexion.rollback()
    finally:
        conexion.close()


def presentes_del_dia(grupo_id: int) -> list:
    """Devuelve los miembros del grupo con sus datos básicos (id, nombre, racha, puntos)."""
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.nombre, u.racha, u.puntos
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
                """,
                (grupo_id,)
            )
            miembros = cursor.fetchall()
            return [dict(row) for row in miembros]
    except Exception as e:
        logging.error(f"Error al obtener miembros del grupo {grupo_id}: {e}")
        return []
    finally:
        conexion.close()