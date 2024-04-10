class Usuario:
    def __init__(self, id_usuario, nombre, email, password, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol

    def __repr__(self):
        return f"Usuario(id={self.id_usuario}, nombre={self.nombre}, email={self.email}, rol={self.rol})"

class Tarea:
    def __init__(self, id_tarea, titulo, descripcion, fecha_entrega, prioridad, usuario_id):
        self.id_tarea = id_tarea
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_entrega = fecha_entrega
        self.prioridad = prioridad
        self.usuario_id = usuario_id

    def __repr__(self):
        return f"Tarea(id={self.id_tarea}, titulo={self.titulo}, fecha_entrega={self.fecha_entrega}, prioridad={self.prioridad}, usuario_id={self.usuario_id})"
