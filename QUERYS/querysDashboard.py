from db import get_connection
import logging

def get_info_usuario(usuario_id: int) -> dict:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    id,
                    nombre,
                    email,
                    avatar,
                    fecha_nacimiento,
                    rol
                FROM usuarios
                WHERE id = %s
            """, (usuario_id,))
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error al obtener info usuario: {e}")
        return None
    finally:
        connection.close()


def get_grupos_usuario(usuario_id: int) -> list:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    g.id,
                    g.nombre,
                    g.descripcion,
                    (
                        SELECT COUNT(*) 
                        FROM grupo_miembros 
                        WHERE grupo_id = g.id
                    ) AS total_miembros
                FROM grupos g
                INNER JOIN grupo_miembros gm ON gm.grupo_id = g.id
                WHERE gm.usuario_id = %s
            """, (usuario_id,))
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener los grupos del usuario: {e}")
        return []
    finally:
        connection.close()


def get_medallas_usuario(usuario_id: int) -> list:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
                ORDER BY um.fecha_obtencion DESC
            """, (usuario_id,))
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener medallas: {e}")
        return []
    finally:
        connection.close()
