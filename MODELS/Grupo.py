from datetime import datetime

class Grupo:
    def __init__(self, nombre : str, descripcion : str | None , admin_id : int, codigo_invitacion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.admin_id = admin_id
        self.codigo_invitacion = codigo_invitacion
        self.fecha_creacion = datetime.now()
        
    def to_tuple(self) -> tuple:
        return (
            self.nombre,
            self.descripcion,
            self.admin_id,
            self.codigo_invitacion,
            self.fecha_creacion
        )


class GrupoMiembro:
    def __init__(self, grupo_id : int, usuario_id : int):
        self.grupo_id = grupo_id
        self.usuario_id = usuario_id
        self.fecha_union = datetime.now()
        
    def to_tuple(self) -> tuple:
        return (
            self.grupo_id,
            self.usuario_id,
            self.fecha_union
        )