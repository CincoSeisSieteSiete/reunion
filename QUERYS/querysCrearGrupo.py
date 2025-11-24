from DB.conexion import get_connection
from MODELS.Grupo import Grupo, GrupoMiembro
import logging

def querys_verificar_limite_crear_grupos(admin_id: int) -> bool:
    connection = get_connection()
    LIMITE_GRUPOS = 5
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM grupos as g
                WHERE g.admin_id = %s;
            """, (admin_id,))
            
            result = cursor.fetchone()
            total_grupos = result['total']
            
            return total_grupos > LIMITE_GRUPOS
            
    except Exception as e:
        logging.error(f"Error al verificar límite de grupos: {e}")
        return False
    finally:
        connection.close()
        

def querys_crear_grupo(grupo : Grupo) -> int:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO grupos (nombre, descripcion, admin_id, 
                codigo_invitacion, 	fecha_creacion) VALUES (%s, %s, %s, %s, %s)""",
                grupo.to_tuple()
            )
            connection.commit()
            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Error al crear el grupo: {e}")
        connection.rollback()
        return -1
    finally:
        connection.close()
    
    
def querys_agregar_admin(miembro : GrupoMiembro) -> None:
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                    "INSERT INTO grupo_miembros (grupo_id, usuario_id, fecha_union) VALUES (%s, %s, %s)",
                    miembro.to_tuple()
                )
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al crear el grupo: {e}")
        connection.rollback()
    finally:
        connection.close()