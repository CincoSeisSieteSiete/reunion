from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
from QUERYS.queryLogin import get_usuario
from QUERYS.queryUsuario import get_info, Update_info
from QUERYS.querysRegistro import create_user
from QUERYS.queryGrupo import get_grupo_info, get_miembros_grupo
from QUERYS.querysDashboard import get_grupos_usuario, get_medallas_usuario
from QUERYS.querysUnirGrupo import unir_usuario_a_grupo, registro_asistencia
from QUERYS.queryPuntos import update_puntos
from QUERYS.queryAsistencias import get_asistencia_usuario
from QUERYS.querysRaking import get_50_posiciones_raking
from QUERYS.querysAdmin import modificar_rangos_usuario_grupo
from QUERYS.querysCumpleanos import get_cumpleanos
from MODELS.Usuario import Usuario, UsuarioLogin, UsuarioConfigurable
from MODELS.Grupo import Grupo


"""Se esta trabajando para las querys en conexion/querys.py y no en este archivo
   por lo que algunas funciones pueden estar duplicadas temporalmente."""

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


def obtener_usuario_por_email(email: str) -> Optional[UsuarioLogin | None]:
    """Obtiene un usuario por email"""
    return get_usuario(email)


def obtener_usuario_por_id(usuario_id: int) -> Optional[Usuario | None]:
    """Obtiene un usuario por id"""
    return get_info(usuario_id)


def crear_usuario(nombre: str, email: str, contraseña: str, fecha_nacimiento: str) -> Tuple[bool, str]:
    """Crea un nuevo usuario"""
    if not nombre or not email or not contraseña or not fecha_nacimiento:
        return False, "Todos los campos son obligatorios"
    
    u = Usuario(1, nombre, email, contraseña, fecha_nacimiento, 'miembro')
    if not (r := create_user(u)):
        return r, "no se pudo crear usuario"
    
    return True, "Usuario creado exitosamente"
    


def obtener_grupo_por_id(grupo_id: int) -> Optional[Grupo | None]:
    """Obtiene un grupo por id"""
    return get_grupo_info(grupo_id)


def obtener_grupos_usuario(usuario_id: int) -> list:
    """Obtiene los grupos a los que pertenece un usuario"""
    return get_grupos_usuario(usuario_id)


#No hagamos esto weon esto es error de seguridad
#def obtener_todos_los_grupos() -> list:
    """Obtiene todos los grupos"""
    #conexion = obtener_conexion()
    #try:
        #with conexion.cursor() as cursor:
            #cursor.execute("""
            #    SELECT g.*, u.nombre AS nombre_admin, COUNT(gm.usuario_id) AS cantidad_miembros
            #    FROM grupos g
            #    LEFT JOIN usuarios u ON g.admin_id = u.id
            #    LEFT JOIN grupo_miembros gm ON g.id = gm.grupo_id
            #    GROUP BY g.id
            #    ORDER BY g.fecha_creacion DESC
            #""")"""
            #return cursor.fetchall()
    #finally:
        #conexion.close()


def unirse_a_grupo(usuario_id: int, codigo_invitacion: str) -> Tuple[bool, str]:
    """Añade un usuario a un grupo usando código de invitación"""
    return unir_usuario_a_grupo(usuario_id, codigo_invitacion)
    

#Verificar bien si fecha es con str o DateTime
def registrar_asistencia(usuario_id: int, grupo_id: int, presente: bool) -> Tuple[bool, str]:
    """Registra la asistencia de un usuario"""
    if presente:
        update_puntos(usuario_id, grupo_id)

    return registro_asistencia(usuario_id, grupo_id, presente)
    

def obtener_asistencias_usuario(usuario_id: int, grupo_id: Optional[int] = None) -> list:
    """Obtiene las asistencias de un usuario"""
    return get_asistencia_usuario(usuario_id)


def obtener_miembros_grupo(grupo_id: int) -> list:
    """Obtiene los miembros de un grupo"""
    return get_miembros_grupo(grupo_id)


def obtener_ranking_global() -> list:
    """Obtiene el ranking global de puntos"""
    return get_50_posiciones_raking()


def obtener_medallas_usuario(usuario_id: int) -> list:
    """Obtiene las medallas de un usuario"""
    return get_medallas_usuario(usuario_id)

def cambiar_rol_usuario(usuario_id: int, rol_id: int, admin_id: int) -> Tuple[bool, str]:
    """Cambia el rol de un usuario (solo admin)"""
    return modificar_rangos_usuario_grupo(usuario_id, rol_id, admin_id)
    


def cambiar_contraseña_usuario(usuario_id: int, nueva_contraseña: str, admin_id: int) -> Tuple[bool, str]:
    """Cambia la contraseña de un usuario (solo admin)"""
    
    if not nueva_contraseña or len(nueva_contraseña) < 6:
        return [False, "Contraseña inválida (mínimo 6 caracteres)"]
    
    resultado = Update_info()
    
    return [resultado, "Contraseña actualizada" if resultado else "no se pudo modificar la contraseña"]



def obtener_cumpleaños_proximos(grupo_id : int, dias: int = 7) -> list:
    """Obtiene los cumpleaños próximos"""
    return get_cumpleanos(grupo_id, dias)
