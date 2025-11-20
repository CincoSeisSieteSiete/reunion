from DB.conexion import get_connection
import logging
from datetime import datetime

def update_puntos(usuario_id : int, grupo_id : int) -> None:
    connection = get_connection()
    maximo_dias_pasado = 7
    try:
        with connection.cursor() as cursor:
            
            fecha_actual = datetime.now()
            cursor.execute("""
        SELECT fecha FROM asistencias 
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
        """, (usuario_id, grupo_id, fecha_actual))
            
            fecha_anterior = cursor.fetchone()
            
            dias_pasados = (fecha_anterior['fecha'] - fecha_actual).day
            es_menor_7_dias = dias_pasados <= maximo_dias_pasado
            
            if es_menor_7_dias:
                cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s",
                           (usuario_id,))
            else:
                cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
            
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        return None
    finally:
        connection.close()
        
        
def gestion_puntos_usuario(puntos : int, usuario_id : int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET puntos = puntos + %s WHERE id = %s",
                           (puntos, usuario_id))
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        return None
    finally:
        connection.close()
    