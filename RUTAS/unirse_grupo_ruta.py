from flask import render_template, request, redirect, url_for, flash, session
from QUERYS.querysUnirGrupo import obtener_grupo_por_codigo, unir_usuario_a_grupo
from QUERYS.queryGrupo import get_esta_grupo

def unirse_grupo_rutas():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        usuario_id = session.get('user_id')

        # Buscar grupo por codigo
        grupo = obtener_grupo_por_codigo(codigo)

        if not grupo:
            flash("Código de invitación inválido.", "error")
            return redirect(url_for('unirse_grupo'))

        grupo_id = grupo['id']

        # Verificar si ya está dentro
        if get_esta_grupo(usuario_id, grupo_id):
            flash("Ya estás en este grupo.", "warning")
            return redirect(url_for('ver_grupo', grupo_id=grupo_id))

        # Unirse al grupo
        if unir_usuario_a_grupo(usuario_id, grupo_id):
            flash("Te uniste correctamente al grupo.", "success")
            return redirect(url_for('ver_grupo', grupo_id=grupo_id))
        else:
            flash("Error al unirte al grupo.", "error")
            return redirect(url_for('unirse_grupo'))

    return render_template('user_view/unirse_grupo.html')
