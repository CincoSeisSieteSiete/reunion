from flask import request, redirect, url_for, flash
from DB.conexion import get_connection
import logging

def editar_rol():
    user_id = request.form.get("user_id")
    rol_id = request.form.get("rol_id")

    if not user_id or not rol_id:
        flash("Datos incompletos.", "error")
        return redirect("/admin")  # Redirige a la página de admin

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET rol_id = %s WHERE id = %s", (rol_id, user_id))
            connection.commit()
        flash("Rol actualizado correctamente.", "success")
    except Exception as e:
        logging.error(f"Error al actualizar rol: {e}")
        flash("Ocurrió un error al actualizar el rol.", "error")
    finally:
        if connection:
            connection.close()

    return redirect("/admin")