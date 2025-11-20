from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from RUTAS import register_ruta
import secrets
from datetime import datetime, timedelta
from datetime import date

from DB.conexion import get_connection

from MODELS.Grupo import Grupo
from QUERYS.querysCrearGrupo import querys_crear_grupo, querys_agregar_admin, GrupoMiembro


def crear_grupo_rutas():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre del grupo es obligatorio', 'danger')
            return redirect(url_for('crear_grupo'))
        
        # Generar código de invitación único
        codigo = secrets.token_urlsafe(8)
        
        #Crear el grupo 
        grupo = Grupo(nombre, descripcion, session['user_id'], codigo)
        grupo_id = querys_crear_grupo(grupo)
        
        if grupo_id == -1:
            flash('Error al crear el grupo', 'danger')
            return redirect(url_for('crear_grupo'))
        
        # Agregar al admin como miembro del grupo
        miembro = GrupoMiembro(grupo_id, session['user_id'])
        querys_agregar_admin(miembro)
        flash(f'Grupo creado exitosamente. Código de invitación: {codigo}', 'success')
        return redirect(url_for('ver_grupo', grupo_id=grupo_id, tema=1))
    
    return render_template('creador/crear_grupo.html')