import pymysql
from pymysql.cursors import DictCursor
import os
from datetime import datetime


# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'asistencias_db'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

"""
DB_CONFIG = {
    'host': 'nioyfp.mysql.pythonanywhere-services.com',
    'user': 'nioyfp',
    'password': 'Jz@#589&<python>',  # 🔒 tu contraseña real
    'database': 'nioyfp$asistencias_db',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}
"""
def get_connection():
    """Obtiene una conexión a la base de datos"""
    return pymysql.connect(**DB_CONFIG)

def init_db():
    """Crea las tablas si no existen"""
    # Primero conectar sin especificar la base de datos para crearla si no existe
    config_without_db = DB_CONFIG.copy()
    db_name = config_without_db.pop('database')
    
    connection = pymysql.connect(**config_without_db)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.commit()
    finally:
        connection.close()
    
    # Ahora conectar a la base de datos creada
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    puntos INT DEFAULT 0,
                    racha INT DEFAULT 0,
                    rol ENUM('admin', 'usuario') DEFAULT 'usuario',
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
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
            
            # Tabla de invitaciones (registro de uso)
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
            
        connection.commit()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    init_db()
