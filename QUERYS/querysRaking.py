from DB.conexion import get_connection
from MODELS.Usuario import Usuario
import logging
from typing import List

def get_50_posiciones_raking() -> List[Usuario]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND presente = TRUE) as total_asistencias
                FROM usuarios u
                ORDER BY u.puntos DESC, u.racha DESC
                LIMIT 50
            """)
            ranking_data = cursor.fetchall()
            ranking = []
            for usuario in ranking_data:
                u = Usuario.from_dict(usuario)
                ranking.append(u)
            return ranking
    except Exception as e:
        logging.error(f"Error fetching ranking data: {e}")
        return []
    finally:
        connection.close()