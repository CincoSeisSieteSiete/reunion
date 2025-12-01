# 🗄️ Documentación de Base de Datos - Proyecto Betania

## Información General

- **Motor**: MySQL 5.7+ / MariaDB 10.3+
- **Charset**: utf8mb4_unicode_ci
- **Base de Datos**: `asistencias_db`

## Diagrama ER

```
usuarios ──┬─→ grupos (admin_id)
           ├─→ grupo_miembros
           ├─→ asistencias
           └─→ usuarios_medallas

grupos ──┬─→ grupo_miembros
         ├─→ asistencias
         └─→ invitaciones

medallas ──→ usuarios_medallas

roles ──→ usuarios (rol_id)
```

## Tablas

### 1. roles
Define los niveles de permisos del sistema.

```sql
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Datos iniciales:**
```sql
INSERT INTO roles (nombre) VALUES ('usuario'), ('lider'), ('admin');
```

### 2. usuarios
Almacena información de todos los usuarios.

```sql
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `puntos` int(11) DEFAULT 0,
  `racha` int(11) DEFAULT 0,
  `tema` bit(1) DEFAULT 0,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `rol_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`),
  KEY `idx_puntos` (`puntos`),
  KEY `fk_rol` (`rol_id`),
  CONSTRAINT `fk_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Campos importantes:**
- `password`: Hash bcrypt (Werkzeug)
- `puntos`: Sistema de gamificación
- `racha`: Días consecutivos de asistencia
- `tema`: 0 = claro, 1 = oscuro

### 3. grupos
Representa grupos/comunidades.

```sql
CREATE TABLE `grupos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `admin_id` int(11) NOT NULL,
  `codigo_invitacion` varchar(20) NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_invitacion` (`codigo_invitacion`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `grupos_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Campos importantes:**
- `admin_id`: Creador del grupo
- `codigo_invitacion`: Código único para unirse

### 4. grupo_miembros
Relación muchos-a-muchos entre usuarios y grupos.

```sql
CREATE TABLE `grupo_miembros` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grupo_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_union` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_miembro` (`grupo_id`,`usuario_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `grupo_miembros_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `grupo_miembros_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5. asistencias
Registra la asistencia de usuarios a grupos.

```sql
CREATE TABLE `asistencias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `grupo_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `presente` tinyint(1) DEFAULT 1,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_asistencia` (`usuario_id`,`grupo_id`,`fecha`),
  KEY `grupo_id` (`grupo_id`),
  KEY `idx_fecha` (`fecha`),
  CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `asistencias_ibfk_2` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Restricción:** Un usuario solo puede tener una asistencia por día por grupo.

### 6. medallas
Sistema de logros/reconocimientos.

```sql
CREATE TABLE `medallas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `imagen` varchar(255) NOT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 7. usuarios_medallas
Relación muchos-a-muchos entre usuarios y medallas.

```sql
CREATE TABLE `usuarios_medallas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `medalla_id` int(11) NOT NULL,
  `fecha_obtencion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_usuario_medalla` (`usuario_id`,`medalla_id`),
  KEY `medalla_id` (`medalla_id`),
  CONSTRAINT `usuarios_medallas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuarios_medallas_ibfk_2` FOREIGN KEY (`medalla_id`) REFERENCES `medallas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 8. invitaciones
Códigos de invitación a grupos.

```sql
CREATE TABLE `invitaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `grupo_id` int(11) NOT NULL,
  `usado_por` int(11) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `fecha_uso` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `grupo_id` (`grupo_id`),
  KEY `usado_por` (`usado_por`),
  KEY `idx_codigo` (`codigo`),
  CONSTRAINT `invitaciones_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invitaciones_ibfk_2` FOREIGN KEY (`usado_por`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 9. admin_logs
Registro de acciones administrativas.

```sql
CREATE TABLE `admin_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` int(11) NOT NULL,
  `accion` varchar(255) NOT NULL,
  `objetivo_id` int(11) NOT NULL,
  `detalle` text DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Consultas Comunes

### Obtener grupos de un usuario

```sql
SELECT g.* 
FROM grupos g
INNER JOIN grupo_miembros gm ON g.id = gm.grupo_id
WHERE gm.usuario_id = ?;
```

### Ranking global de usuarios

```sql
SELECT u.id, u.nombre, u.puntos, u.racha
FROM usuarios u
ORDER BY u.puntos DESC
LIMIT 10;
```

### Asistencias de un grupo en un mes

```sql
SELECT u.nombre, a.fecha, a.presente
FROM asistencias a
INNER JOIN usuarios u ON a.usuario_id = u.id
WHERE a.grupo_id = ?
  AND MONTH(a.fecha) = ?
  AND YEAR(a.fecha) = ?
ORDER BY a.fecha DESC;
```

### Miembros de un grupo con sus puntos

```sql
SELECT u.id, u.nombre, u.puntos, u.racha
FROM usuarios u
INNER JOIN grupo_miembros gm ON u.id = gm.usuario_id
WHERE gm.grupo_id = ?
ORDER BY u.puntos DESC;
```

## Índices y Optimización

- **Índices únicos**: `email`, `codigo_invitacion`, `(usuario_id, grupo_id, fecha)`
- **Índices de búsqueda**: `idx_email`, `idx_puntos`, `idx_fecha`, `idx_codigo`
- **Claves foráneas**: Todas con `ON DELETE CASCADE` para integridad referencial

## Instalación

```bash
# Crear base de datos
mysql -u root -p < SQL.sql

# O manualmente
mysql -u root -p
CREATE DATABASE asistencias_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE asistencias_db;
source SQL.sql;

# Insertar roles
INSERT INTO roles (nombre) VALUES ('usuario'), ('lider'), ('admin');
```

---

**Desarrollado por**: Niozex Studio
