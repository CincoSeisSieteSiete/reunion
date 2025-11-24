# db.py
import pymysql
from pymysql.cursors import DictCursor
from CONFIGURACION.config import data

def get_connection():
    """
    Devuelve una conexión a la base de datos.
    Usa DictCursor por defecto.
    """
    """return pymysql.connect(
        host=data['host'],
        user=data['user'],
        password=data['password'],
        database=data['database'],
        charset=data.get('charset', 'utf8mb4'),
        cursorclass=DictCursor
    )"""
    #Conexión local
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='asistencias_db',
        charset='utf8mb4',
        cursorclass=DictCursor
    )



if __name__ == "__main__":
    # Prueba de conexión
    try:
        conn = get_connection()
        print("✅ Conexión exitosa a la base de datos")
        conn.close()
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
