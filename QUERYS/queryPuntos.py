from DB.conexion import get_connection
import logging
from datetime import date


def update_puntos(usuario_id: int, grupo_id: int) -> None:
    """Actualiza la racha y los puntos del usuario según su última asistencia.
    Si no hay asistencia previa, se considera la primera asistencia.
    """
    connection = get_connection()
    maximo_dias_pasado = 7
    try:
        with connection.cursor() as cursor:
            # Fecha actual sin hora
            fecha_actual = date.today()
            # Obtener la última asistencia anterior a hoy donde el usuario estuvo presente
            cursor.execute(
                """
                SELECT fecha FROM asistencias
                WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
                ORDER BY fecha DESC LIMIT 1
                """,
                (usuario_id, grupo_id, fecha_actual)
            )
            resultado = cursor.fetchone()
            if resultado:
                fecha_anterior = resultado['fecha']
                dias_pasados = (fecha_actual - fecha_anterior).days
                es_menor_7_dias = dias_pasados <= maximo_dias_pasado
                if es_menor_7_dias:
                    cursor.execute(
                        "UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s",
                        (usuario_id,)
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s",
                        (usuario_id,)
                    )
            else:
                # Primera asistencia del usuario
                cursor.execute(
                    "UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s",
                    (usuario_id,)
                )
            connection.commit()
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        connection.rollback()
    finally:
        connection.close()


def gestion_puntos_usuario(puntos: int, usuario_id: int):
    """Incrementa los puntos del usuario en la cantidad especificada."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET puntos = puntos + %s
                WHERE id = %s
                """,
                (puntos, usuario_id)
            )
            connection.commit()
    except Exception as e:
        logging.error(f"Error al actualizar puntos: {e}")
        connection.rollback()
    finally:
        connection.close()


def remove_puntos(usuario_id: int, grupo_id: int) -> None:
    """Remueve 10 puntos y reinicia la racha a 0 cuando se elimina una asistencia.
    No permite que los puntos queden negativos.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET puntos = GREATEST(puntos - 10, 0), racha = 0
                WHERE id = %s
                """,
                (usuario_id,)
            )
            connection.commit()
    except Exception as e:
        logging.error(f"Error al remover puntos: {e}")
        connection.rollback()
    finally:
        connection.close()