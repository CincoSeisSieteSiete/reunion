from flask import render_template, request
from datetime import datetime, date
from calendar import monthrange
from QUERYS.querysCumpleanos import get_cumpleanos

def cumpleanos_rutas(id_grupo: int):
    # Fecha actual
    hoy_real = date.today()

    # Obtener mes y año desde parámetros GET, si no vienen usar mes actual
    try:
        mes_solicitado = int(request.args.get('mes', hoy_real.month))
        year_solicitado = int(request.args.get('year', hoy_real.year))
    except:  # noqa: E722
        mes_solicitado = hoy_real.month
        year_solicitado = hoy_real.year

    # Validar fecha
    try:
        fecha_inicio_mes = date(year_solicitado, mes_solicitado, 1)
    except:  # noqa: E722
        fecha_inicio_mes = hoy_real
        mes_solicitado = hoy_real.month
        year_solicitado = hoy_real.year

    # Obtener cumpleaños del grupo
    cumpleanos_todos = get_cumpleanos(id_grupo)

    cumpleanos_json = []
    cumple_hoy = []

    if cumpleanos_todos:
        for u in cumpleanos_todos:
            fecha = u['fecha_nacimiento']
            if not fecha or fecha == '0000-00-00':
                continue
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            # JSON seguro
            cumpleanos_json.append({
                "nombre": u["nombre"],
                "mes": fecha.month,
                "dia": fecha.day
            })

        # Cumpleaños de hoy
        cumple_hoy = [
            u for u in cumpleanos_json
            if u['mes'] == hoy_real.month and u['dia'] == hoy_real.day
        ]

    # Datos para el calendario
    dias_mes = monthrange(year_solicitado, mes_solicitado)[1]

    return render_template(
        'user_view/cumpleanos.html',
        cumpleanos_data=cumpleanos_json,
        cumple_hoy=cumple_hoy,
        mes_actual=mes_solicitado,
        year_actual=year_solicitado,
        hoy_real=hoy_real,
        dias_mes=dias_mes,
        fecha_inicio_mes=fecha_inicio_mes
    )
