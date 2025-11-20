# Sistema de Asistencias para Reuniones Cristianas

Sistema web gamificado de toma de asistencias desarrollado con Flask y PyMySQL.

## Características

- **Gestión de Usuarios**: Registro, login y perfiles personalizados
- **Grupos**: Creación y administración de grupos con códigos de invitación
- **Asistencias**: Registro de asistencias con actualización automática de rachas
- **Gamificación**: Sistema de puntos, rachas y medallas
- **Ranking**: Tabla de clasificación con destacados oro, plata y bronce
- **Panel Admin**: Herramientas completas para administradores

## Instalación

1. Instalar dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Configurar variables de entorno:
\`\`\`bash
cp .env.example .env
# Editar .env con tus credenciales de MySQL
\`\`\`

3. Crear carpeta para medallas:
\`\`\`bash
mkdir -p static/medallas
\`\`\`

4. Inicializar la base de datos:
\`\`\`bash
python db.py
\`\`\`

5. Ejecutar la aplicación:
\`\`\`bash
python app.py
\`\`\`

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

\`\`\`
/
├── app.py                 # Aplicación principal Flask
├── db.py                  # Configuración y esquema de base de datos
├── requirements.txt       # Dependencias Python
├── .env.example          # Ejemplo de variables de entorno
├── static/
│   └── medallas/         # Imágenes de medallas (PNG/SVG)
└── templates/            # Plantillas HTML con Jinja2
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── grupo.html
    ├── crear_grupo.html
    ├── unirse_grupo.html
    ├── tomar_asistencia.html
    ├── gestionar_puntos.html
    ├── gestionar_medallas.html
    ├── perfil.html
    └── ranking.html
\`\`\`

## Uso

### Para Usuarios:
1. Registrarse en el sistema
2. Unirse a grupos usando códigos de invitación
3. Ver perfil con puntos, rachas y medallas
4. Consultar ranking de clasificación

### Para Administradores:
1. Crear grupos y generar códigos de invitación
2. Tomar asistencia de los miembros
3. Gestionar puntos manualmente
4. Crear y asignar medallas
5. Ver estadísticas del grupo

## Base de Datos

El sistema crea automáticamente las siguientes tablas:
- `usuarios` - Información de usuarios
- `grupos` - Grupos de reuniones
- `grupo_miembros` - Relación usuarios-grupos
- `asistencias` - Registro de asistencias
- `medallas` - Catálogo de medallas
- `usuarios_medallas` - Medallas obtenidas por usuarios
- `invitaciones` - Historial de invitaciones

## Tecnologías

- **Backend**: Flask (Python)
- **Base de Datos**: MySQL con PyMySQL
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Plantillas**: Jinja2




# Ideas Futuras [No significa que se hagan]

- Modo oscuro/claro
- Rangos de usuario / Insignias
    - Creyente
    - Disipulo
    - servidor 
- Banners para tu perfil
- Medallas [Esta si]
- Economia
    - Poder gastar tus puntos.
        - Poder abonar un arbol que creesca
        - Comprar banners
        - Temas para tu perfil
    - hacer votaciones
        - Poder gastar el puntos para vota por tu Lider favorito
        - Eventos futuros para hacer
    
