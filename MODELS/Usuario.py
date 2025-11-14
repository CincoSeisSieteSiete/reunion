class Usuario:
    def __init__(self, id, nombre, email, password, fecha_nacimiento, rol_id):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.fecha_nacimiento = fecha_nacimiento
        self.rol_id = rol_id
    
    def to_tuple(self):
        return (self.id, self.nombre, self.email, self.password, self.fecha_nacimiento, self.rol_id)