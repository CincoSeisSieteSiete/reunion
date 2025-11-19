from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from DB.conexion import get_connection
from QUERYS.querysRaking import get_50_posiciones_raking


def ranking_global_rutas():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.nombre, u.puntos, u.racha,
                       (SELECT COUNT(*) FROM usuarios_medallas WHERE usuario_id = u.id) as total_medallas,
                       (SELECT COUNT(*) FROM asistencias WHERE usuario_id = u.id AND presente = TRUE) as total_asistencias
                FROM usuarios u
                ORDER BY u.puntos DESC, u.racha DESC
                LIMIT 50
            """)
            ranking = get_50_posiciones_raking()
            
            return render_template('user_view/ranking.html', ranking=ranking)
    finally:
        connection.close()