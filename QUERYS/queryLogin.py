from DB.conexion import get_connection
from MODELS.Grupo import Grupo
import logging
from MODELS.Usuario import UsuarioLogin
from MODELS.Usuario import UsuarioDict as UD

def get_usuario(email: str) -> UsuarioLogin:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.email = %s
            """, (email,))
            result = cursor.fetchone()
            u = UsuarioLogin(
                    id=result[UD.id],
                    nombre=result[UD.nombre],
                    email=result[UD.email],
                    password=result[UD.password],
                    fecha_nacimiento=result[UD.fecha_nacimiento])
            return u
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()