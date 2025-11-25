from DB.conexion import get_connection
import logging
from MODELS.Usuario import UsuarioDict as UD

def modificar_rangos_usuario_grupo(id_grupo: int, id_usuario: int, nuevo_rango: int) -> bool:
    """Actualiza el rango (rol) de un usuario dentro de un grupo.
    Devuelve True si la operación fue exitosa, False en caso contrario.
    """
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM grupo_miembros
                WHERE grupo_id = %s AND usuario_id = %s
                """,
                (id_grupo, id_usuario)
            )
            usuario = cursor.fetchone()
            if not usuario:
                logging.warning(f"El usuario {id_usuario} no es miembro del grupo {id_grupo}.")
                return False
            # Actualizar el rol del usuario en la tabla de miembros
            cursor.execute(
                """
                UPDATE grupo_miembros SET rol_id = %s WHERE usuario_id = %s AND grupo_id = %s
                """,
                (nuevo_rango, id_usuario, id_grupo)
            )
            connection.commit()
            return True
    except Exception as e:
        logging.error(f"Error al modificar rangos del usuario en el grupo: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def es_admin(grupo_id: int, admin_id: int) -> bool:
    """Comprueba si el usuario con admin_id es administrador del grupo especificado."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT admin_id FROM grupos WHERE id = %s", (grupo_id,))
            grupo = cursor.fetchone()
            return grupo is not None and grupo['admin_id'] == admin_id
    except Exception as e:
        logging.error(f"Error al verificar admin del grupo: {e}")
        return False
    finally:
        connection.close()

def es_lider_global(user_id: int) -> bool:
    """Devuelve True si el usuario tiene rol global de 'admin' o 'lider'."""
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                rol = cursor.fetchone()
                return rol is not None and rol['nombre'] in ('admin', 'lider')
            return False
    except Exception as e:
        logging.error(f"Error verificando rol global: {e}")
        return False
    finally:
        connection.close()
