from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import db
from datetime import datetime, timedelta
from datetime import date
from QUERYS.querysDashboard import *

def dashboard_rutas(request):
    connection = db.get_connection()
    try:
        user_id = session['user_id']
        user = get_info_usuario(user_id)
            
        # Mostrar panel si no tiene fecha de nacimiento
        mostrar_panel_cumple = not user['fecha_nacimiento']

        # Guardar fecha si viene del form
        if request.method == 'POST' and 'fecha_nacimiento' in request.form:
            nueva_fecha = request.form['fecha_nacimiento']    
            update_fecha_nacimiento(user_id, nueva_fecha)
            user['fecha_nacimiento'] = nueva_fecha
            mostrar_panel_cumple = False

            # Grupos
            grupos = get_grupos_usuario(user_id)

            # Medallas
            medallas = get_medallas_usuario(user_id)

            # Cumpleaños del mes de los miembros de los grupos del usuario
            mes_actual = date.today().month
            cumpleanos_mes = get_cumpleanos_mes(user_id, mes_actual)
            
        return render_template('dashboard.html', 
        user=user, grupos=grupos,
        medallas=medallas,
        mostrar_panel_cumple=mostrar_panel_cumple,
        cumpleanos_mes=cumpleanos_mes)
        
    finally:
        connection.close()