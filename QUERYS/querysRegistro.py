from DB.conexion import get_connection
from MODELS.Grupo import *
import logging
from MODELS.Usuario import Usuario

def user_exists(email) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            return cursor.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking user existence: {e}")
        return False
    finally:
        connection.close()
        
def get_default_role_id() -> int:
    connection = get_connection()
    DEFAULT = 2
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM roles WHERE nombre = 'usuario'")
            rol = cursor.fetchone()
            return rol['id'] if rol else DEFAULT  # fallback si no existe
    except Exception as e:
        logging.error(f"Error fetching default role id: {e}")
        return DEFAULT
    finally:
        connection.close()
        
def create_user(usuario : Usuario) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, rol_id) VALUES (%s, %s, %s, %s, %s)",
                usuario.to_tuple()[1:]  # Exclude id for insertion
            )
            connection.commit()
            return True
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return False
    finally:
        connection.close()