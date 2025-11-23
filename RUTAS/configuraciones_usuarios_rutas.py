from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from DB.conexion import get_connection
from werkzeug.security import generate_password_hash

configuraciones_usuarios_rutas = Blueprint('configuraciones_usuarios', __name__)

@configuraciones_usuarios_rutas.route('/configuracion')
def configuracion():
    return render_template('config/config.html')

@configuraciones_usuarios_rutas.route('/configuracion/cuenta', methods=['GET', 'POST'])
def cuenta():
    user_id = session.get('user_id')  # Asegúrate de que guardas el ID del usuario en sesión
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        if password:
            password_hash = generate_password_hash(password)
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, email=%s, password=%s WHERE id=%s",
                (nombre, email, password_hash, user_id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, email=%s WHERE id=%s",
                (nombre, email, user_id)
            )
        conn.commit()
        flash("Datos actualizados correctamente", "success")
        conn.close()
        return redirect(url_for('configuraciones_usuarios.cuenta'))

    # GET: obtener datos actuales del usuario
    cursor.execute("SELECT nombre, email FROM usuarios WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('config/cuenta.html', user=user)