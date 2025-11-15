# db.py
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    'host': 'nioyfp.mysql.pythonanywhere-services.com',
    'user': 'nioyfp',
    'password': 'Jz@#589&<python>',
    'database': 'nioyfp$asistencias_db',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)
