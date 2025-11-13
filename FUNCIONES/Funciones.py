from werkzeug.security import generate_password_hash
from datetime import datetime

def actualizar_racha_y_puntos(cursor, usuario_id, grupo_id, fecha_actual):
    """Actualiza la racha y puntos del usuario"""
    cursor.execute("""
        SELECT fecha FROM asistencias 
        WHERE usuario_id = %s AND grupo_id = %s AND presente = TRUE AND fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (usuario_id, grupo_id, fecha_actual))
    
    ultima_asistencia = cursor.fetchone()
    fecha_obj = datetime.strptime(fecha_actual, '%Y-%m-%d').date()
    
    if ultima_asistencia:
        ultima_fecha = ultima_asistencia['fecha']
        diferencia = (fecha_obj - ultima_fecha).days
        if diferencia <= 7:
            cursor.execute("UPDATE usuarios SET racha = racha + 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
        else:
            cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))
    else:
        cursor.execute("UPDATE usuarios SET racha = 1, puntos = puntos + 10 WHERE id = %s", (usuario_id,))

def hash_password(password):
    return generate_password_hash(password)
