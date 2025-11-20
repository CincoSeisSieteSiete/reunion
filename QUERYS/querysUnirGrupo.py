from DB.conexion import get_connection
import logging
from queryGrupo import get_esta_grupo
from typing import Tuple
from datetime import datetime


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


def unir_usuario_a_grupo(usuario_id: int , codigo_invitacion : str) -> Tuple[bool, str]:
    """ Inserta al usuario dentro del grupo """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM grupos WHERE codigo_invitacion = %s", 
                           (codigo_invitacion,))
            grupo = cursor.fetchone()
            
            if not grupo:
                return [False, "Código de invitación inválido"]
            
            grupo_id = grupo['id']
            
            if get_esta_grupo(grupo_id, usuario_id):
                return [False, "Ya eres miembro de este grupo"]
            
            cursor.execute("""
                INSERT INTO grupo_miembros (usuario_id, grupo_id)
                VALUES (%s, %s)
            """, (usuario_id, grupo_id))
        connection.commit()
        
        return [True, "Te has unido al grupo exitosamente"]
    except Exception as e:
        logging.error(f"Error uniendo a grupo: {e}")
        return [False, "Error de que no se pudo unir al grupo"]
    finally:
        connection.close()
        

def registro_asistencia(usuario_id: int, grupo_id: int, presente: bool) -> Tuple[bool, str]:
    conexion = get_connection()
    try:
        fecha = datetime.now()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO asistencias (usuario_id, grupo_id, fecha, presente)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE presente = VALUES(presente)
            """, (usuario_id, grupo_id, fecha, presente))
            cursor.commit()
            
            return [True, "Asistencia registrada"]
    except Exception as e:
        logging.error(f"error al registrar asistencia: {e}")
        return [False, "Hubo un error al subir los datos"]
    finally:
        conexion.close()
    pass