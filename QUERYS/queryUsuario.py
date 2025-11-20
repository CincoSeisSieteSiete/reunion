from DB.conexion import get_connection
import logging
from MODELS.Usuario import Usuario, UsuarioConfigurable, UsuarioDict as UD

def Update_info(usuario : UsuarioConfigurable, usuario_id : int) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            UPDATE usuarios
            SET nombre = %s,
                email = %s,
                password = %s,
                fecha_nacimiento = %s,
            WHERE id = %s
            """, usuario.to_tuple() + (usuario_id,))

            connection.commit()
            
            return True

    except Exception as e:
        logging.error(f"Error al actualizar la información del usuario: {e}")
        return False
    finally:
        connection.close()

    return True

def get_info(usuario_id : int) -> Usuario | None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT id, nombre, email, password, fecha_nacimiento
            FROM usuarios
            WHERE id = %s
            """, (usuario_id,))

            result = cursor.fetchone()
            if result:
                return Usuario(
                    id=result[UD.id],
                    nombre=result[UD.nombre],
                    email=result[UD.email],
                    password=result[UD.password],
                    fecha_nacimiento=result[UD.fecha_nacimiento]
                )
            else:
                logging.info(f"No se encontró el usuario con id {usuario_id}")
                return None

    except Exception as e:
        logging.error(f"Error al obtener la información del usuario: {e}")
        return None
    finally:
        connection.close()


def get_users_medallas() -> list:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nombre, email FROM usuarios ORDER BY nombre")
            usuarios = cursor.fetchall()
            return usuarios
    except Exception as e:
        logging.error(f"error al agregar medalla: {e}")
        return []
    finally:
        connection.close()