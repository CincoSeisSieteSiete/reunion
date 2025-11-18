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
            sql = """
                INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, rol_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            hashed_password = generate_password_hash(usuario.password)
            data = (
                usuario.nombre,
                usuario.email,
                hashed_password,
                usuario.fecha_nacimiento.strftime("%Y-%m-%d") if usuario.fecha_nacimiento else None,
                usuario.rol_id or get_default_role_id()
            )
            print("Insertando usuario con datos:", data)
            cursor.execute(sql, data)
            connection.commit()
            print("Usuario registrado correctamente")
            return True
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return False
    finally:
        connection.close()
