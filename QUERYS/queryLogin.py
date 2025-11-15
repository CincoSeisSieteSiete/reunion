from DB.conexion import get_connection
from MODELS.Grupo import Grupo
import logging

def get_usuario(email: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.email = %s
            """, (email,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()