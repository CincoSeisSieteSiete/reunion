from DB.conexion import get_connection
import logging

def get_asistencia_usuario(usuario_id : int) -> list:
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                    SELECT * FROM asistencias
                    WHERE usuario_id = %s
                    ORDER BY fecha DESC
                """, (usuario_id,))
            asistencias = cursor.fetchall()
            return asistencias['asistenias']
    finally:
        conexion.close()