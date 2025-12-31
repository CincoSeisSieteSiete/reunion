from DB.conexion import get_connection
from MODELS.Usuario import Usuario
import logging
from werkzeug.security import generate_password_hash

def user_exists(email) -> bool:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            return cursor.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking user existence: {e}")
        return False
    finally:
        connection.close()

def get_default_role_id() -> int:
    connection = get_connection()
    DEFAULT = 2
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM roles WHERE nombre = 'usuario'")
            rol = cursor.fetchone()
            return rol['id'] if rol else DEFAULT
    except Exception as e:
        logging.error(f"Error fetching default role id: {e}")
        return DEFAULT
    finally:
        connection.close()

def create_user(usuario: Usuario) -> bool:
    if user_exists(usuario.email):
        print("El usuario ya existe")
        return False

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Aseguramos que el SQL incluya genero_id
            sql = """
                INSERT INTO usuarios (nombre, email, password, genero_id, fecha_nacimiento, rol_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            hashed_password = generate_password_hash(usuario.password)
            
            # Formateamos la fecha si existe
            fecha_nac = usuario.fecha_nacimiento.strftime("%Y-%m-%d") if usuario.fecha_nacimiento else None
            
            # Importante: Asegúrate de que genero_id sea un int o None
            genero = int(usuario.genero_id) if usuario.genero_id else None
            
            data = (
                usuario.nombre,
                usuario.email,
                hashed_password,
                genero, 
                fecha_nac,
                usuario.rol_id or get_default_role_id()
            )
            
            print(f"Insertando usuario: {usuario.email} con Género ID: {genero}")
            
            cursor.execute(sql, data)
            connection.commit()
            return True
            
    except Exception as e:
        print(f"Error creando usuario: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()