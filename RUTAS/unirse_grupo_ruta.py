from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from RUTAS import register_ruta
import db
import secrets
from datetime import datetime, timedelta
from datetime import date
import os
from QUERYS.querysUnirGrupo import *

def unirse_grupo_rutas():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        
        connection = db.get_connection()
        try:
            # Buscar grupo por código
            grupo = get_grupo_code(codigo)
                
            if not grupo:
                flash('Código de invitación inválido', 'danger')
                return redirect(url_for('unirse_grupo'))
                
            # Verificar si ya es miembro
            isMember = IsMember(grupo['id'], session['user_id'])  
            if isMember:
                flash('Ya eres miembro de este grupo', 'info')
                return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
                
            # Agregar como miembro
            if not add_member_to_group(grupo['id'], session['user_id']):
                flash('Error al unirse al grupo', 'danger')
                return redirect(url_for('unirse_grupo'))
                
                # Registrar uso de invitación
            if not register_invitation_use(codigo, grupo['id'], session['user_id']):
                flash('Error al registrar el uso de la invitación', 'danger')
                return redirect(url_for('unirse_grupo'))
                
            flash('Te has unido al grupo exitosamente', 'success')
            return redirect(url_for('ver_grupo', grupo_id=grupo['id']))
        finally:
            connection.close()
    
    return render_template('unirse_grupo.html')