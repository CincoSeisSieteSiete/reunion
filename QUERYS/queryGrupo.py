from DB.conexion import get_connection
from MODELS.Grupo import *
import logging
from MODELS.Grupo import * 

def get_esta_grupo(grupo_id, usuario_id) -> bool:
    """
    Verifica si un usuario es miembro de un grupo específico.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as es_miembro 
                FROM grupo_miembros 
                WHERE grupo_id = %s AND usuario_id = %s
            """, (grupo_id, usuario_id))
            result = cursor.fetchone()
            return result['es_miembro'] > 0
    except Exception as e:
        logging.error(f"Error checking group membership: {e}")
        return False
    finally:
        connection.close()
    
def get_grupo_info(grupo_id) -> Grupo:
    """
    Obtiene la información de un grupo específico.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT g.*, u.nombre as admin_nombre
                FROM grupos g
                INNER JOIN usuarios u ON g.admin_id = u.id
                WHERE g.id = %s
            """, (grupo_id,))
            grupo = cursor.fetchone()
            return grupo
    except Exception as e:
        logging.error(f"Error fetching group info: {e}")
        return None
    finally:
        connection.close()
        
        
def get_raking_grupo(grupo_id) -> list:
    """
    Obtiene el ranking de los miembros de un grupo específico.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND grupo_id = %s AND presente = TRUE) as asistencias_grupo
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.puntos DESC, u.racha DESC
            """, (grupo_id, grupo_id))
            ranking = cursor.fetchall()
            return ranking
    except Exception as e:
        logging.error(f"Error fetching group ranking: {e}")
        return []
    finally:
        connection.close()