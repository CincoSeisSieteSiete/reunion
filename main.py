from app import crear_aplicacion
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """Punto de entrada de la aplicación"""
    
    aplicacion = crear_aplicacion()
    
    puerto = 5000
    debug = True
    host = '127.0.0.30' #'0.0.0.0'
    
    aplicacion.run(debug=debug, host=host, port=puerto)


if __name__ == '__main__':
    main()
