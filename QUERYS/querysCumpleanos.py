from datetime import date, datetime
import calendar
from DB.conexion import get_connection
import logging

def get_cumpleanos(id_grupo: int) -> list:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    u.id, 
                    u.nombre, 
                    u.fecha_nacimiento,
                    DAY(u.fecha_nacimiento) AS dia,
                    MONTH(u.fecha_nacimiento) AS mes
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                AND u.fecha_nacimiento IS NOT NULL
                ORDER BY mes, dia
            """, (id_grupo,))

            return cursor.fetchall()

    except Exception as e:
        logging.error(f"Error al obtener cumpleaños: {e}")
        return []
    finally:
        connection.close()
