class Usuario:
    def __init__(self, id=None, nombre=None, email=None, password=None, 
                 fecha_nacimiento=None, rol_id=None, tema=None, puntos=None, 
                 racha=None, fecha_registro=None, reset_token=None, reset_expires=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.fecha_nacimiento = fecha_nacimiento
        self.rol_id = rol_id
        self.tema = tema
        self.puntos = puntos if puntos else 0
        self.racha = racha if racha else 0
        self.fecha_registro = fecha_registro
        self.reset_token = reset_token
        self.reset_expires = reset_expires
    
    def to_tuple(self):
        return (self.id, self.nombre, self.email, self.password, 
                self.fecha_nacimiento, self.rol_id, self.tema, self.puntos, 
                self.racha, self.fecha_registro, self.reset_token, self.reset_expires)
    
    @classmethod
    def from_dict(cls, data):
        """Crea un Usuario desde un diccionario de la BD"""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            email=data.get('email'),
            password=data.get('password'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            rol_id=data.get('rol_id'),
            tema=data.get('tema') or data.get('TEMA'),  # Maneja ambos casos
            puntos=data.get('puntos') if data.get('puntos') else 0,
            racha=data.get('racha') if data.get('racha') else 0,
            fecha_registro=data.get('fecha_registro'),
            reset_token=data.get('reset_token'),
            reset_expires=data.get('reset_expires')
        )
    
    def to_dict(self):
        """Convierte el Usuario a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'password': self.password,
            'fecha_nacimiento': self.fecha_nacimiento,
            'rol_id': self.rol_id,
            'tema': self.tema,
            'puntos': self.puntos,
            'racha': self.racha,
            'fecha_registro': self.fecha_registro,
            'reset_token': self.reset_token,
            'reset_expires': self.reset_expires
        }
    
    
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
    tema = 'TEMA'