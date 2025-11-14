from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import db


def ranking_global_rutas():
    connection = db.get_connection()
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
            ranking = cursor.fetchall()
            
            return render_template('ranking.html', ranking=ranking)
    finally:
        connection.close()