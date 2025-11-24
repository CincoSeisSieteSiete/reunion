from DB.conexion import get_connection
import logging
from MODELS.Usuario import UsuarioDict as UD

def modificar_rangos_usuario_grupo(id_grupo: int, id_usuario: int, nuevo_rango : int) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT * FROM grupo_miembros
            WHERE grupo_id = %s AND usuario_id = %s
            """, (id_grupo, id_usuario))
            
            usuario = cursor.fetchone()
            if not usuario:
                logging.warning(f"El usuario {id_usuario} no es miembro del grupo {id_grupo}.")
                return False
            
            #string magico donde debemos agregarlo en una clase para no repetir codigo y evitar errores
            usuario[UD.rol_id] = nuevo_rango
            
            cursor.execute("""
                           uppdate usuario set rol_id = %s
                           WHERE id = %s
                           """, (nuevo_rango, id_usuario))

            connection.commit()
            
            return True

    except Exception as e:
        logging.error(f"Error al modificar rangos del usuario en el grupo: {e}")
        connection.rollback()
        return False
from DB.conexion import get_connection
import logging
from MODELS.Usuario import UsuarioDict as UD

def modificar_rangos_usuario_grupo(id_grupo: int, id_usuario: int, nuevo_rango : int) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT * FROM grupo_miembros
            WHERE grupo_id = %s AND usuario_id = %s
            """, (id_grupo, id_usuario))
            
            usuario = cursor.fetchone()
            if not usuario:
                logging.warning(f"El usuario {id_usuario} no es miembro del grupo {id_grupo}.")
                return False
            
            #string magico donde debemos agregarlo en una clase para no repetir codigo y evitar errores
            usuario[UD.rol_id] = nuevo_rango
            
            cursor.execute("""
                           uppdate usuario set rol_id = %s
                           WHERE id = %s
                           """, (nuevo_rango, id_usuario))

            connection.commit()
            
            return True

    except Exception as e:
        logging.error(f"Error al modificar rangos del usuario en el grupo: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

    return True


def es_admin(grupo_id : int, admin_id : int)-> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT admin_id FROM grupos WHERE admin_id = %s AND id = %s", 
            (admin_id,grupo_id))
            grupo = cursor.fetchone()
<<<<<<< Updated upstream
=======
            # Retorna True si es el admin del grupo
>>>>>>> Stashed changes
            return grupo is not None and grupo['admin_id'] == admin_id
    except Exception as e:
        logging.error(f"Error al verificar admin del grupo: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def es_lider_global(user_id: int) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT rol_id FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute("SELECT nombre FROM roles WHERE id = %s", (user['rol_id'],))
                rol = cursor.fetchone()
                if rol and rol['nombre'] in ['admin', 'lider']:
                    return True
    except Exception as e:
        logging.error(f"Error verificando rol global: {e}")
    finally:
        connection.close()
    return False