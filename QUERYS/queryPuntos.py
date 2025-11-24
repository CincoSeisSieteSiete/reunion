from DB.conexion import get_connection
import logging
from datetime import datetime, date

def update_puntos(usuario_id: int, grupo_id: int) -> None:
    connection = get_connection()
    maximo_dias_pasado = 7
    try:
        with connection.cursor() as cursor:
            
<<<<<<< Updated upstream
            fecha_actual = datetime.now().date()

=======
            # Obtener fecha actual (solo DATE, sin hora)
            fecha_actual = date.today()
            
            # Buscar la última asistencia ANTERIOR a hoy
>>>>>>> Stashed changes
            cursor.execute("""
                SELECT fecha FROM asistencias 
                WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
                ORDER BY fecha DESC LIMIT 1
            """, (usuario_id, grupo_id, fecha_actual))
            
<<<<<<< Updated upstream
            fecha_anterior = cursor.fetchone()

            dias_pasados = 0

            if fecha_anterior is not None:
                dias_pasados = (fecha_anterior['fecha'] - fecha_actual).days
            
            es_menor_7_dias = dias_pasados <= maximo_dias_pasado
            
            if es_menor_7_dias:
                cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s",
                           (usuario_id,))
=======
            resultado = cursor.fetchone()
            
            # Si hay asistencia anterior, verificar racha
            if resultado:
                fecha_anterior = resultado['fecha']
                
                # Calcular días transcurridos
                dias_pasados = (fecha_actual - fecha_anterior).days
                es_menor_7_dias = dias_pasados <= maximo_dias_pasado
                
                if es_menor_7_dias:
                    # Mantiene racha
                    cursor.execute("""
                        UPDATE usuarios 
                        SET racha = racha + 1, puntos = puntos + 10 
                        WHERE id = %s
                    """, (usuario_id,))
                else:
                    # Reinicia racha
                    cursor.execute("""
                        UPDATE usuarios 
                        SET racha = 1, puntos = puntos + 10 
                        WHERE id = %s
                    """, (usuario_id,))
>>>>>>> Stashed changes
            else:
                # Primera asistencia, iniciar racha
                cursor.execute("""
                    UPDATE usuarios 
                    SET racha = 1, puntos = puntos + 10 
                    WHERE id = %s
                """, (usuario_id,))
            
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        connection.rollback()
    finally:
        connection.close()
        
        
def gestion_puntos_usuario(puntos: int, usuario_id: int):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE usuarios 
                SET puntos = puntos + %s 
                WHERE id = %s
            """, (puntos, usuario_id))
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        connection.rollback()
    finally:
        connection.close()


def remove_puntos(usuario_id: int, grupo_id: int) -> None:
    """
    Remueve puntos y ajusta la racha cuando se quita una asistencia.
    Resta 10 puntos y reinicia la racha a 0.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Restar 10 puntos y resetear racha (no puede ser negativo)
            cursor.execute("""
                UPDATE usuarios 
                SET puntos = GREATEST(puntos - 10, 0), racha = 0
                WHERE id = %s
            """, (usuario_id,))
            connection.commit()
            
    except Exception as e:
        logging.error(f"Error al remover puntos: {e}")
        connection.rollback()
    finally:
        connection.close()