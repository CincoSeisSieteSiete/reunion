from flask import request, redirect, url_for
import os

def subir_imagen_medalla_ruta(app):
    """
    Lógica para subir una imagen de medalla al servidor.
    Guarda la imagen en static/medallas con el nombre especificado.
    """
    imagen = request.files.get('imagen')
    nombre_imagen = request.form.get('nombre_imagen')
    
    if not imagen or not nombre_imagen:
        return "Error: faltan datos", 400
    
    # Obtener extensión original (.png, .jpg, etc.)
    extension = os.path.splitext(imagen.filename)[1]
    nuevo_nombre = f"{nombre_imagen}{extension}"
    
    # Crear ruta de la carpeta de medallas
    ruta_carpeta = os.path.join(app.static_folder, 'medallas')
    os.makedirs(ruta_carpeta, exist_ok=True)
    
    # Guardar la imagen
    ruta_archivo = os.path.join(ruta_carpeta, nuevo_nombre)
    imagen.save(ruta_archivo)
    
    return redirect(url_for('gestionar_medallas'))
