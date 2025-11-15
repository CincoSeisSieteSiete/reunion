from flask import render_template, request
import db
from datetime import datetime, date
from calendar import monthrange
from QUERYS.querysCumpleanos import get_cumpleanos

def cumpleanos_rutas():
    connection = db.get_connection()
    cumpleanos_json = []
    cumple_hoy = []

    # Obtener mes y año solicitados por URL o usar actuales
    try:
        mes_solicitado = int(request.args.get('mes', date.today().month))
        year_solicitado = int(request.args.get('year', date.today().year))
    except:
        mes_solicitado = date.today().month
        year_solicitado = date.today().year

    # Validar fecha
    try:
        fecha_contexto = date(year_solicitado, mes_solicitado, 1)
    except:
        fecha_contexto = date.today()
        mes_solicitado = fecha_contexto.month
        year_solicitado = fecha_contexto.year
        
    

    try:
        cumpleanos_todos = get_cumpleanos()
        
        if(not cumpleanos_todos):
            raise Exception("No se pudieron obtener los cumpleaños")
        
        # Convertir strings → date y filtrar fechas inválidas
        for u in cumpleanos_todos:
            fecha = u['fecha_nacimiento']
            if not fecha or fecha == '0000-00-00':
                u['fecha_nacimiento'] = None
                continue
            if isinstance(fecha, str):
                u['fecha_nacimiento'] = datetime.strptime(fecha, "%Y-%m-%d").date()

            hoy_real = date.today()

            # Cumpleaños de hoy
            cumple_hoy = [
                u for u in cumpleanos_todos
                if u['fecha_nacimiento'] is not None and
                   u['fecha_nacimiento'].month == hoy_real.month and
                   u['fecha_nacimiento'].day == hoy_real.day
            ]

            # Construir JSON seguro para el frontend
            for u in cumpleanos_todos:
                if u['fecha_nacimiento'] is not None:
                    cumpleanos_json.append({
                        "nombre": u["nombre"],
                        "mes": u["fecha_nacimiento"].month,
                        "dia": u["fecha_nacimiento"].day
                    })
    except Exception as e:
        print(f"Error al obtener cumpleaños: {e}")
        cumpleanos_json = []
        cumple_hoy = []

    # Datos para el calendario
    dias_mes = monthrange(year_solicitado, mes_solicitado)[1]
    fecha_inicio_mes = date(year_solicitado, mes_solicitado, 1)

    return render_template(
        'cumpleanos.html',
        cumpleanos_data=cumpleanos_json,
        cumple_hoy=cumple_hoy,
        mes_actual=mes_solicitado,
        year_actual=year_solicitado,
        hoy_real=hoy_real,
        dias_mes=dias_mes,
        fecha_inicio_mes=fecha_inicio_mes
    )
