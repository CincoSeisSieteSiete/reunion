from DB.conexion import get_connection
import logging
from datetime import datetime

def get_asistencia_usuario(usuario_id : int) -> list:
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                    SELECT * FROM asistencias
                    WHERE usuario_id = %s
                    ORDER BY fecha DESC
                """, (usuario_id,))
            asistencias = cursor.fetchall()
            return asistencias
    except Exception as e:
        logging.error(f"error al dar asistencia: {e}")
    finally:
        conexion.close()
        
def insertar_asistencia(usuario_id : int, grupo_id : int, presente : bool) -> None:
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            fecha = datetime.now()
            cursor.execute("""
                        INSERT INTO asistencias (usuario_id, grupo_id, fecha, presente)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE presente = %s
                    """, (usuario_id, grupo_id, fecha, presente))
            conexion.commit()
    except Exception as e:
        logging.error(f"error al insertar asistencia: {e}")
    finally:
        conexion.close()
        
def presentes_del_dia(grupo_id : int) -> None:
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.racha, u.puntos
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            miembros = cursor.fetchall()
            return miembros
    except Exception as e:
        logging.error(f"error al insertar asistencia: {e}")
    finally:
        conexion.close()