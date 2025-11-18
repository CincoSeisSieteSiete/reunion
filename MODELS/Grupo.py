from datetime import datetime

class Grupo:
    def __init__(self, nombre, descripcion, admin_id, codigo_invitacion, creado_por=None, fecha_creacion=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.admin_id = admin_id
        self.codigo_invitacion = codigo_invitacion
        self.creado_por = creado_por if creado_por is not None else admin_id
        self.fecha_creacion = fecha_creacion if fecha_creacion is not None else datetime.now()

    def to_tuple(self):
        return (
            self.nombre,
            self.descripcion,
            self.admin_id,
            self.codigo_invitacion,
            self.fecha_creacion
        )


class GrupoMiembro:
    def __init__(self, grupo_id, usuario_id, fecha_union=None):
        self.grupo_id = grupo_id
        self.usuario_id = usuario_id
        self.fecha_union = fecha_union if fecha_union is not None else datetime.now()

    def to_tuple(self):
        return (
            self.grupo_id,
            self.usuario_id,
            self.fecha_union
        )
