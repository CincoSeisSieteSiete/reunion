from DB.conexion import get_connection
from MODELS.Grupo import *
import logging

def get_cumpleanos():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, nombre, fecha_nacimiento
                FROM usuarios
                WHERE fecha_nacimiento IS NOT NULL
                ORDER BY DAY(fecha_nacimiento)
            """)
            cumpleanos_todos = cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener cumpleaños: {e}")
        return []
    finally:
        connection.close()
        
    return cumpleanos_todos

