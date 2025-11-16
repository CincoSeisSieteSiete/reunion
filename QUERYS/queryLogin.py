from DB.conexion import get_connection
import logging

def get_usuario(email: str):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM usuarios
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()
