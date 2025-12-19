# Configuración de la base de datos MySQL Local

import os

# Configuración de la base de datos MySQL Local
"""
data ={
  "host": "localhost",
  "user": "root",
  "password": "",
  "database": "asistencias_db",
  "charset": "utf8mb4",
  "cursorclass": "DictCursor"
}

# Configuración para despliegue en PythonAnywhere
data ={
  "host": "nioyfp.mysql.pythonanywhere-services.com",
  "user": "nioyfp",
  "password": "Jz@#589&<python>",
  "database": "nioyfp$asistencias_db",
  "charset": "utf8mb4",
  "cursorclass": "DictCursor"
}
"""

# Facebook OAuth settings (set via environment variables)
# PowerShell example:
# $env:FACEBOOK_CLIENT_ID='your-id'; $env:FACEBOOK_CLIENT_SECRET='your-secret'
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID', '881029631032282')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET', '')
FACEBOOK_API_VERSION = os.environ.get('FACEBOOK_API_VERSION', 'v15.0')


# Configuración para despliegue en PythonAnywhere
data ={
  "host": "nioyfp.mysql.pythonanywhere-services.com",
  "user": "nioyfp",
  "password": "Jz@#589&<python>",
  "database": "nioyfp$asistencias_db",
  "charset": "utf8mb4",
  "cursorclass": "DictCursor"
}

