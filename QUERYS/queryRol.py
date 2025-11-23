from DB.conexion import get_connection
import logging

def get_rol_name(rol_id : int) -> str:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.nombre
                FROM roles as r 
                WHERE r.rol_id = 1 = %s
            """, (rol_id,))
            rol_data = cursor.fetchone()
            name = rol_data['nombre']
            return name
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        connection.close()