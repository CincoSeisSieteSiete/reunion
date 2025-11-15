from DB.conexion import get_connection
from MODELS.Grupo import Grupo
import logging
from MODELS.Grupo import GrupoMiembro

def get_grupo_code(codigo_invitacion : str) -> Grupo | None:
    connection = get_connection()
    grupo = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM grupos WHERE codigo_invitacion = %s", (codigo_invitacion,))
            result = cursor.fetchone()
            if result:
                grupo = Grupo(
                    id=result['id'],
                    nombre=result['nombre'],
                    descripcion=result['descripcion'],
                    codigo_invitacion=result['codigo_invitacion'],
                    creado_por=result['creado_por'],
                    fecha_creacion=result['fecha_creacion']
                )
    except Exception as e:
        logging.error(f"Error al obtener el grupo por código: {e}")
    finally:
        connection.close()
    return grupo

def IsMember(grupo_id: int, usuario_id: int) -> bool:
    connection = get_connection()
    is_member = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM grupo_miembros WHERE grupo_id = %s AND usuario_id = %s",
                (grupo_id, usuario_id)
            )
            if cursor.fetchone():
                is_member = True
    except Exception as e:
        logging.error(f"Error al verificar si el usuario es miembro del grupo: {e}")
    finally:
        connection.close()
    return is_member

def add_member_to_group(grupo_id: int, usuario_id: int) -> bool:
    connection = get_connection()
    success = False
    try:
        with connection.cursor() as cursor:
            grupo = GrupoMiembro(
                grupo_id=grupo_id,
                usuario_id=usuario_id
            )
            cursor.execute(
                "INSERT INTO grupo_miembros (grupo_id, usuario_id, fecha_union) VALUES (%s, %s, %s)",
                grupo.to_tuple()
            )
            connection.commit()
            success = True
    except Exception as e:
        logging.error(f"Error al agregar miembro al grupo: {e}")
    finally:
        connection.close()
    return success

def register_invitation_use(codigo: str, grupo_id: int, usuario_id: int) -> bool:
    connection = get_connection()
    success = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO invitaciones (codigo, grupo_id, usado_por, fecha_uso) VALUES (%s, %s, %s, NOW())",
                (codigo, grupo_id, usuario_id)
            )
            connection.commit()
            success = True
    except Exception as e:
        logging.error(f"Error al registrar el uso de la invitación: {e}")
    finally:
        connection.close()
    return success