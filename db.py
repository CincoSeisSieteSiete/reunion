import pymysql
from CONFIGURACION.config import data

def get_connection():
    return pymysql.connect(
        host=data['host'],
        user=data['user'],
        password=data['password'],
        database=data['database'],
        charset=data.get('charset', 'utf8mb4'),
        cursorclass=pymysql.cursors.DictCursor  # aquí sí va la clase
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Conexión exitosa a la base de datos.")
        conn.close()
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
