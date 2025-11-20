from datetime import date, datetime
import calendar
from DB.conexion import get_connection
import logging

def get_cumpleanos(id_grupo: int, days: int = 7) -> list:
    """
    Obtiene cumpleaños próximos de miembros de un grupo.
    
    Args:
        id_grupo: ID del grupo
        days: Días hacia adelante para buscar (default 7)
    
    Returns:
        Lista de usuarios con cumpleaños próximos
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    u.id, 
                    u.nombre, 
                    u.email,
                    u.fecha_nacimiento,
                    DAY(u.fecha_nacimiento) AS dia,
                    MONTH(u.fecha_nacimiento) AS mes,
                    DATE_ADD(
                        DATE(u.fecha_nacimiento), 
                        INTERVAL YEAR(CURDATE()) - YEAR(DATE(u.fecha_nacimiento)) YEAR
                    ) AS cumple_este_ano
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                AND u.fecha_nacimiento IS NOT NULL
                AND DATE_ADD(
                    DATE(u.fecha_nacimiento), 
                    INTERVAL YEAR(CURDATE()) - YEAR(DATE(u.fecha_nacimiento)) YEAR
                ) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                ORDER BY cumple_este_ano
            """, (id_grupo, days))

            return cursor.fetchall()

    except Exception as e:
        logging.error(f"Error al obtener cumpleaños próximos: {e}")
        return []
    finally:
        connection.close()