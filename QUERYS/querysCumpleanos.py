from DB.conexion import get_connection
import logging

def get_cumpleanos(id_grupo: int) -> list:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT u.id, u.nombre, u.fecha_nacimiento 
            FROM usuarios u
            INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
            WHERE gm.grupo_id = %s
            AND u.fecha_nacimiento IS NOT NULL
            """, (id_grupo,))

        cumpleanos_todos = cursor.fetchall()

        if not cumpleanos_todos:
            logging.info(f"No hay miembros con fecha de nacimiento en el grupo con id {id_grupo}")
            return []
            
    except Exception as e:
        logging.error(f"Error al obtener cumpleaños: {e}")
        return []
    finally:
        connection.close()
        
    return cumpleanos_todos

