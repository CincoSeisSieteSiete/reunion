from DB.conexion import get_connection
import logging

def agregar_medalla(nombre, descripcion, imagen) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                        "INSERT INTO medallas (nombre, descripcion, imagen) VALUES (%s, %s, %s)",
                        (nombre, descripcion, imagen)
                    )
            connection.commit()
            return True
    except Exception as e:
        logging.error(f"error al agregar medalla: {e}")
        return False
    finally:
        connection.close()
        
def asignar_medalla(usuario_id : int, medalla_id : int) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                        "INSERT IGNORE INTO usuarios_medallas (usuario_id, medalla_id) VALUES (%s, %s)",
                        (usuario_id, medalla_id)
                    )
            connection.commit()
            return True
    except Exception as e:
        logging.error(f"error al asignar medalla: {e}")
        return False
    finally:
        connection.close()
        
   
def eliminar_medalla(medalla_id : int) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM medallas WHERE id = %s", (medalla_id,))
            connection.commit()
            return True
    except Exception as e:
        logging.error(f"error al agregar medalla: {e}")
        return False
    finally:
        connection.close()  

def get_medallas() -> list:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM medallas ORDER BY fecha_creacion DESC")
            medallas = cursor.fetchall()
            return medallas
    except Exception as e:
        logging.error(f"error al agregar medalla: {e}")
        return []
    finally:
        connection.close() 
        
        
def get_medallas_of_user(user_id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*, um.fecha_obtencion
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (user_id,))
            medallas = cursor.fetchall()
            
            return medallas
        
    except Exception as e:
        logging.error(f"error al agregar medalla: {e}")
        return []
    finally:
        connection.close() 