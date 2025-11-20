from DB.conexion import get_connection
import logging
from MODELS.Usuario import Usuario, UsuarioConfigurable, UsuarioDict as UD

def Update_info(usuario : UsuarioConfigurable, usuario_id : int) -> bool:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            # Construir dinámicamente la consulta SQL solo con los campos que no son None
            campos_actualizar = []
            valores = []
            
            if usuario.nombre is not None:
                campos_actualizar.append("nombre = %s")
                valores.append(usuario.nombre)
            
            if usuario.email is not None:
                campos_actualizar.append("email = %s")
                valores.append(usuario.email)
            
            if usuario.password is not None:
                campos_actualizar.append("password = %s")
                valores.append(usuario.password)
            
            if usuario.fecha_nacimiento is not None:
                campos_actualizar.append("fecha_nacimiento = %s")
                valores.append(usuario.fecha_nacimiento)
            
            # Si no hay campos para actualizar, retornar False
            if not campos_actualizar:
                logging.warning(f"No hay campos para actualizar en el usuario {usuario_id}")
                return False
            
            # Agregar el ID al final de los valores
            valores.append(usuario_id)
            
            # Construir la consulta dinámicamente
            sql = f"""
            UPDATE usuarios
            SET {', '.join(campos_actualizar)}
            WHERE id = %s
            """
            
            cursor.execute(sql, tuple(valores))
            connection.commit()
            
            
            
            return True

    except Exception as e:
        logging.error(f"Error al actualizar la información del usuario: {e}")
        return False
    finally:
        connection.close()

def get_info(usuario_id : int) -> Usuario | None:
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT id, nombre, email, password, fecha_nacimiento
            FROM usuarios
            WHERE id = %s
            """, (usuario_id,))

            result = cursor.fetchone()
            if result:
                return Usuario(
                    id=result[UD.id],
                    nombre=result[UD.nombre],
                    email=result[UD.email],
                    password=result[UD.password],
                    fecha_nacimiento=result[UD.fecha_nacimiento]
                )
            else:
                logging.info(f"No se encontró el usuario con id {usuario_id}")
                return None

    except Exception as e:
        logging.error(f"Error al obtener la información del usuario: {e}")
        return None
    finally:
        connection.close()
