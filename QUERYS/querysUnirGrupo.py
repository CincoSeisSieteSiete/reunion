from DB.conexion import get_connection
import logging


def limite_union_grupos(usuario_id : int) -> bool:
    connection = get_connection()
    LIMITE_GRUPOS = 100
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM grupo_miembros as gm
                WHERE gm.usuario_id = %s;
            """, (usuario_id,))
            
            result = cursor.fetchone()
            total_grupos = result['total']
            
            return total_grupos > LIMITE_GRUPOS
    except Exception as e:
        logging.error(f"Error obteniendo grupo por código: {e}")
        return None
    finally:
        connection.close()


def obtener_grupo_por_codigo(codigo):
    """ Retorna el grupo si el código existe """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM grupos 
                WHERE codigo_invitacion = %s
            """, (codigo,))
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error obteniendo grupo por código: {e}")
        return None
    finally:
        connection.close()


def ya_esta_en_el_grupo(usuario_id, grupo_id):
    """ Verifica si el usuario ya es miembro """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total 
                FROM grupo_miembros
                WHERE usuario_id = %s AND grupo_id = %s
            """, (usuario_id, grupo_id))
            result = cursor.fetchone()
            return result['total'] > 0
    except Exception as e:
        logging.error(f"Error revisando membership: {e}")
        return False
    finally:
        connection.close()


def unir_usuario_a_grupo(usuario_id, grupo_id):
    """ Inserta al usuario dentro del grupo """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO grupo_miembros (usuario_id, grupo_id)
                VALUES (%s, %s)
            """, (usuario_id, grupo_id))
        connection.commit()
        return True
    except Exception as e:
        logging.error(f"Error uniendo a grupo: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()
