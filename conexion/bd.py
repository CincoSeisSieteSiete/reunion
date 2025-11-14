import pymysql
from pymysql.cursors import DictCursor
import os
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

CONFIGURACION_BD: Dict[str, str] = {
    'host': 'localhost',#os.getenv('BD_HOST', 'localhost'),
    'user': 'root',#os.getenv('BD_USUARIO', 'root'),
    'password': '',#os.getenv('BD_CONTRASEÑA', ''),
    'database': 'asistencia_db',#os.getenv('BD_NOMBRE', 'asistencias_db'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


def obtener_conexion() -> pymysql.Connection:
    """Obtiene una conexión a la base de datos"""
    return pymysql.connect(**CONFIGURACION_BD)


def obtener_cursor(conexion: pymysql.Connection) -> pymysql.cursors.Cursor:
    """Obtiene un cursor de la conexión"""
    return conexion.cursor()


def ejecutar_consulta(sql: str, parametros: tuple = ()) -> Optional[List[Dict[str, Any]]]:
    """Ejecuta una consulta SELECT y retorna los resultados"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_uno(sql: str, parametros: tuple = ()) -> Optional[Dict[str, Any]]:
    """Ejecuta una consulta SELECT y retorna un solo resultado"""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchone()
    finally:
        conexion.close()


def inicializar_bd() -> None:
    """Crea las tablas si no existen"""
    config_sin_bd = CONFIGURACION_BD.copy()
    nombre_bd = config_sin_bd.pop('database')
    
    conexion = pymysql.connect(**config_sin_bd)
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conexion.commit()
    finally:
        conexion.close()
    
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Tabla de roles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(50) UNIQUE NOT NULL,
                    descripcion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    fecha_nacimiento DATE,
                    puntos INT DEFAULT 0,
                    racha INT DEFAULT 0,
                    rol_id INT DEFAULT 2,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reset_token VARCHAR(255),
                    reset_expires DATETIME,
                    FOREIGN KEY (rol_id) REFERENCES roles(id),
                    INDEX idx_email (email),
                    INDEX idx_puntos (puntos DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de grupos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grupos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    admin_id INT NOT NULL,
                    codigo_invitacion VARCHAR(20) UNIQUE NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    INDEX idx_codigo (codigo_invitacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de miembros de grupos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grupo_miembros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    grupo_id INT NOT NULL,
                    usuario_id INT NOT NULL,
                    fecha_union DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_miembro (grupo_id, usuario_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de asistencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asistencias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    grupo_id INT NOT NULL,
                    fecha DATE NOT NULL,
                    presente BOOLEAN DEFAULT TRUE,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_asistencia (usuario_id, grupo_id, fecha),
                    INDEX idx_fecha (fecha)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de medallas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medallas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    imagen VARCHAR(255) NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de medallas de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_medallas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    medalla_id INT NOT NULL,
                    fecha_obtencion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY (medalla_id) REFERENCES medallas(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_usuario_medalla (usuario_id, medalla_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de invitaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invitaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(20) NOT NULL,
                    grupo_id INT NOT NULL,
                    usado_por INT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_uso DATETIME,
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
                    FOREIGN KEY (usado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
                    INDEX idx_codigo (codigo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Tabla de logs de admin
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    admin_id INT NOT NULL,
                    accion VARCHAR(100) NOT NULL,
                    objetivo_id INT,
                    detalle TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    INDEX idx_fecha (fecha_creacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Insertar roles por defecto
            cursor.execute("SELECT COUNT(*) as count FROM roles")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("INSERT INTO roles (nombre, descripcion) VALUES ('usuario', 'Usuario estándar')")
                cursor.execute("INSERT INTO roles (nombre, descripcion) VALUES ('lider', 'Líder de grupo')")
                cursor.execute("INSERT INTO roles (nombre, descripcion) VALUES ('admin', 'Administrador')")

        conexion.commit()
    except Exception as e:
        conexion.rollback()
        raise e
    finally:
        conexion.close()
