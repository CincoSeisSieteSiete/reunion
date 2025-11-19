from flask import render_template, session
from QUERYS.querysDashboard import get_info_usuario, get_grupos_usuario, get_medallas_usuario
from DB.conexion import get_connection

def dashboard_rutas(request):
    connection = get_connection()
    try:
        user_id = session['user_id']

        user = get_info_usuario(user_id)
        grupos = get_grupos_usuario(user_id)
        medallas = get_medallas_usuario(user_id)

        return render_template(
            "user_view/dashboard.html",
            user=user,
            grupos=grupos,
            medallas=medallas
        )

    finally:
        connection.close()
