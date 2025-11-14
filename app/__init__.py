from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()


def crear_aplicacion() -> Flask:
    """Factory para crear la aplicación Flask"""
    aplicacion = Flask(__name__, 
                      template_folder='../templates',
                      static_folder='../static')
    
    aplicacion.secret_key = os.getenv('SECRET_KEY', 'Nioy')
    
    from app.rutas import registrar_rutas
    registrar_rutas(aplicacion)
    
    return aplicacion
