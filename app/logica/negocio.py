from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
from conexion import obtener_conexion


def generar_codigo_invitacion() -> str:
    """Genera un código de invitación único"""
    import secrets
    return secrets.token_urlsafe(12).upper()[:16]


def generar_hash_contraseña(contraseña: str) -> str:
    """Genera un hash de contraseña"""
    return generate_password_hash(contraseña)


def verificar_contraseña(hash_contraseña: str, contraseña: str) -> bool:
    """Verifica si una contraseña coincide con su hash"""
    return check_password_hash(hash_contraseña, contraseña)


def obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por email"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.email = %s
            """, (email,))
            return cursor.fetchone()
    finally:
        conexion.close()


def obtener_usuario_por_id(usuario_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por id"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.id = %s
            """, (usuario_id,))
            return cursor.fetchone()
    finally:
        conexion.close()


def crear_usuario(nombre: str, email: str, contraseña: str, fecha_nacimiento: str) -> Tuple[bool, str]:
    """Crea un nuevo usuario"""
    if not nombre or not email or not contraseña or not fecha_nacimiento:
        return False, "Todos los campos son obligatorios"
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "El email ya está registrado"
            
            hash_contraseña = generar_hash_contraseña(contraseña)
            cursor.execute("SELECT id FROM roles WHERE nombre = 'usuario'")
            rol = cursor.fetchone()
            rol_id = rol['id'] if rol else 2
            
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password, fecha_nacimiento, rol_id) VALUES (%s, %s, %s, %s, %s)",
                (nombre, email, hash_contraseña, fecha_nacimiento, rol_id)
            )
            conexion.commit()
            return True, "Usuario creado exitosamente"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()


def obtener_grupo_por_id(grupo_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un grupo por id"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT g.*, u.nombre AS nombre_admin
                FROM grupos g
                LEFT JOIN usuarios u ON g.admin_id = u.id
                WHERE g.id = %s
            """, (grupo_id,))
            return cursor.fetchone()
    finally:
        conexion.close()


def obtener_grupos_usuario(usuario_id: int) -> list:
    """Obtiene los grupos a los que pertenece un usuario"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT g.*, u.nombre AS nombre_admin
                FROM grupos g
                LEFT JOIN usuarios u ON g.admin_id = u.id
                INNER JOIN grupo_miembros gm ON g.id = gm.grupo_id
                WHERE gm.usuario_id = %s
                ORDER BY g.fecha_creacion DESC
            """, (usuario_id,))
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_todos_los_grupos() -> list:
    """Obtiene todos los grupos"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT g.*, u.nombre AS nombre_admin, COUNT(gm.usuario_id) AS cantidad_miembros
                FROM grupos g
                LEFT JOIN usuarios u ON g.admin_id = u.id
                LEFT JOIN grupo_miembros gm ON g.id = gm.grupo_id
                GROUP BY g.id
                ORDER BY g.fecha_creacion DESC
            """)
            return cursor.fetchall()
    finally:
        conexion.close()


def unirse_a_grupo(usuario_id: int, codigo_invitacion: str) -> Tuple[bool, str]:
    """Añade un usuario a un grupo usando código de invitación"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id FROM grupos WHERE codigo_invitacion = %s", (codigo_invitacion,))
            grupo = cursor.fetchone()
            
            if not grupo:
                return False, "Código de invitación inválido"
            
            grupo_id = grupo['id']
            
            cursor.execute("""
                SELECT id FROM grupo_miembros 
                WHERE usuario_id = %s AND grupo_id = %s
            """, (usuario_id, grupo_id))
            
            if cursor.fetchone():
                return False, "Ya eres miembro de este grupo"
            
            cursor.execute("""
                INSERT INTO grupo_miembros (grupo_id, usuario_id)
                VALUES (%s, %s)
            """, (grupo_id, usuario_id))
            
            conexion.commit()
            return True, "Te has unido al grupo exitosamente"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()


def registrar_asistencia(usuario_id: int, grupo_id: int, fecha: str, presente: bool) -> Tuple[bool, str]:
    """Registra la asistencia de un usuario"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO asistencias (usuario_id, grupo_id, fecha, presente)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE presente = VALUES(presente)
            """, (usuario_id, grupo_id, fecha, presente))
            
            if presente:
                actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha)
            
            conexion.commit()
            return True, "Asistencia registrada"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()


def actualizar_racha_y_puntos(cursor, usuario_id: int, grupo_id: int, fecha_actual: str) -> None:
    """Actualiza la racha y puntos del usuario"""
    cursor.execute("""
        SELECT fecha FROM asistencias 
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (usuario_id, grupo_id, fecha_actual))
    
    ultima_asistencia = cursor.fetchone()
    fecha_obj = datetime.strptime(fecha_actual, '%Y-%m-%d').date()
    
    if ultima_asistencia:
        ultima_fecha = ultima_asistencia['fecha']
        diferencia = (fecha_obj - ultima_fecha).days
        if diferencia <= 7:
            cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
        else:
            cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
    else:
        cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))


def obtener_asistencias_usuario(usuario_id: int, grupo_id: Optional[int] = None) -> list:
    """Obtiene las asistencias de un usuario"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            if grupo_id:
                cursor.execute("""
                    SELECT * FROM asistencias
                    WHERE usuario_id = %s AND grupo_id = %s
                    ORDER BY fecha DESC
                """, (usuario_id, grupo_id))
            else:
                cursor.execute("""
                    SELECT * FROM asistencias
                    WHERE usuario_id = %s
                    ORDER BY fecha DESC
                """, (usuario_id,))
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_miembros_grupo(grupo_id: int) -> list:
    """Obtiene los miembros de un grupo"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.email, u.puntos, u.racha, u.fecha_nacimiento
                FROM usuarios u
                INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
                WHERE gm.grupo_id = %s
                ORDER BY u.nombre
            """, (grupo_id,))
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_ranking_global() -> list:
    """Obtiene el ranking global de puntos"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, email, puntos, racha, fecha_nacimiento
                FROM usuarios
                ORDER BY puntos DESC
                LIMIT 100
            """)
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_medallas_usuario(usuario_id: int) -> list:
    """Obtiene las medallas de un usuario"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT m.* 
                FROM medallas m
                INNER JOIN usuarios_medallas um ON m.id = um.medalla_id
                WHERE um.usuario_id = %s
            """, (usuario_id,))
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_usuarios_para_admin() -> list:
    """Obtiene todos los usuarios para la vista de admin"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.email, u.puntos, u.racha, u.fecha_nacimiento,
                       u.fecha_registro, u.rol_id, r.nombre AS rol
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                ORDER BY u.id DESC
            """)
            return cursor.fetchall()
    finally:
        conexion.close()


def cambiar_rol_usuario(usuario_id: int, rol_id: int, admin_id: int) -> Tuple[bool, str]:
    """Cambia el rol de un usuario (solo admin)"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nombre FROM roles WHERE id = %s", (rol_id,))
            rol = cursor.fetchone()
            
            if not rol:
                return False, "Rol inválido"
            
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE id = %s", (rol_id, usuario_id))
            
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle)
                VALUES (%s, %s, %s, %s)
            """, (admin_id, 'cambiar_rol', usuario_id, f'nuevo_rol={rol["nombre"]}'))
            
            conexion.commit()
            return True, f"Rol actualizado a {rol['nombre']}"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()


def cambiar_contraseña_usuario(usuario_id: int, nueva_contraseña: str, admin_id: int) -> Tuple[bool, str]:
    """Cambia la contraseña de un usuario (solo admin)"""
    if not nueva_contraseña or len(nueva_contraseña) < 6:
        return False, "Contraseña inválida (mínimo 6 caracteres)"
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            hash_contraseña = generar_hash_contraseña(nueva_contraseña)
            cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (hash_contraseña, usuario_id))
            
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, accion, objetivo_id, detalle)
                VALUES (%s, %s, %s, %s)
            """, (admin_id, 'cambiar_contraseña', usuario_id, 'admin_cambio_contraseña'))
            
            conexion.commit()
            return True, "Contraseña actualizada"
    except Exception as e:
        conexion.rollback()
        return False, str(e)
    finally:
        conexion.close()


def obtener_cumpleaños_proximos(dias: int = 7) -> list:
    """Obtiene los cumpleaños próximos"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, email, fecha_nacimiento
                FROM usuarios
                WHERE DATE_ADD(DATE(fecha_nacimiento), INTERVAL YEAR(CURDATE())-YEAR(DATE(fecha_nacimiento)) YEAR) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                ORDER BY MONTH(fecha_nacimiento), DAY(fecha_nacimiento)
            """, (dias,))
            return cursor.fetchall()
    finally:
        conexion.close()
