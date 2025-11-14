from app import crear_aplicacion
from conexion import inicializar_bd
import os
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """Punto de entrada de la aplicación"""
    try:
        inicializar_bd()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar base de datos: {e}")
    
    aplicacion = crear_aplicacion()
    
    puerto = 5000
    debug = True
    host = '127.0.0.30' #'0.0.0.0'
    
    aplicacion.run(debug=debug, host=host, port=puerto)


if __name__ == '__main__':
    main()
