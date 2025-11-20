from DB.conexion import get_connection
import logging
from MODELS.Usuario import UsuarioDict as UD
from typing import Tuple

def modificar_rangos_usuario_grupo(usuario_id: int, rol_id: int, admin_id: int) -> Tuple[bool, str]:
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nombre FROM roles WHERE id = %s", (rol_id,))
            rol = cursor.fetchone()
            
            if not rol:
                return [False, "Rol inválido"]
            
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE id = %s", (rol_id, usuario_id))
            conexion.commit()
            
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle)
                VALUES (%s, %s, %s, %s)
            """, (admin_id, 'cambiar_rol', usuario_id, f'nuevo_rol={rol["nombre"]}'))
            
            conexion.commit()
            
            return [True, f"Rol actualizado a {rol['nombre']}"]
    except Exception as e:
        logging.error(f"error en admin modificar roles: {e}")
        conexion.rollback()
        return [False, "Error al modificar el rol"]
    finally:
        conexion.close()