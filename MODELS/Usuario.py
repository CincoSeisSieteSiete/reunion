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
    
    
class UsuarioConfigurable:
    def __init__(self, nombre, email, password, fecha_nacimiento):
        self.nombre = nombre
        self.email = email
        self.password = password
        self.fecha_nacimiento = fecha_nacimiento
        
    def to_tuple(self):
        return (self.nombre, self.email, self.password, self.fecha_nacimiento)

class UsuarioDict:
    id = 'id'
    nombre = 'nombre'
    email = 'email'
    password = 'password'
    fecha_nacimiento = 'fecha_nacimiento'
    rol_id = 'rol_id'
    puntos = 'puntos'
    racha = 'racha'
    fecha_registro = 'fecha_registro'
    reset_token = 'reset_token'
    reset_expires = 'reset_expires'