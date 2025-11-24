from flask import render_template, request, redirect, url_for, session, flash
import os
from QUERYS.queryMedallas import agregar_medalla, asignar_medalla, eliminar_medalla, get_medallas
from QUERYS.queryUsuario import get_users_medallas

def gestionar_medallas_ruta(app):
    """
    Lógica para gestionar medallas del sistema.
    Solo accesible para administradores globales.
    """
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'crear':
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            imagen = request.form.get('imagen')
            
            if not agregar_medalla(nombre, descripcion, imagen):
                flash('Fallo al crear medalla', 'error')
            else:
                flash('Medalla creada exitosamente', 'success')
        
        elif accion == 'asignar':
            usuario_id = request.form.get('usuario_id')
            medalla_id = request.form.get('medalla_id')
            
            if not asignar_medalla(usuario_id, medalla_id):
                flash('Fallo al asignar medalla', 'error')
            else:
                flash('Medalla asignada exitosamente', 'success')
        
        elif accion == 'eliminar':
            medalla_id = request.form.get('medalla_id')
            
            if not eliminar_medalla(medalla_id):
                flash('No se pudo eliminar la medalla', 'error')
            else:
                flash('Medalla eliminada exitosamente', 'success')
        
        return redirect(url_for('gestionar_medallas'))
    
    # GET: Obtener datos para mostrar
    medallas = get_medallas()
    usuarios = get_users_medallas()
    
    # Obtener imágenes del directorio static/medallas
    medallas_path = os.path.join(app.root_path, 'static', 'medallas')
    
    # Verificar si el directorio existe
    if os.path.exists(medallas_path):
        imagenes = [f for f in os.listdir(medallas_path) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
    else:
        imagenes = []
    
    return render_template(
        'gestionar/gestionar_medallas.html',
        medallas=medallas,
        usuarios=usuarios,
        imagenes=imagenes,
        tema=1
    )
