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
        return False
    finally:
        connection.close()

    return True