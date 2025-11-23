from DB.conexion import get_connection
import logging
from MODELS.Usuario import Usuario, UsuarioDict as UD

def get_usuario(email: str) -> Usuario:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*
                FROM usuarios u
                WHERE u.email = %s
            """, (email,))
            user_data = cursor.fetchone()
            # Convertir a objeto Usuario
            u = Usuario.from_dict(user_data)
            if not u:
                logging.warning(f"No existe el email {email}")
            return u
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()