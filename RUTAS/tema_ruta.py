from flask import session,request
from DB.conexion import get_connection

def cambiar_tema():
    nuevo_tema = 1 if request.form.get("tema") == "1" else 0   # ← captura del checkbox

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE usuarios SET tema = %s WHERE id = %s",
                (nuevo_tema, session['user_id'])
            )
            connection.commit()

        session['tema'] = nuevo_tema  # ← guardar en la sesión

    finally:
        connection.close()
