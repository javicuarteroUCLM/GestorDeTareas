import sqlite3
from sqlite3 import Error

def conectar_a_base_de_datos(path='sistema_tareas.db'):
    """Método para conectar la base de datos, si no existe la creamos"""
    conexion = None
    try:
        conexion = sqlite3.connect(path)
        print("Conexión exitosa a SQLite")
    except Error as e:
        print(f"Error al conectar a SQLite: {e}")
    return conexion

def crear_tablas(conexion):
    """Método para crear las tablas en la base de datos si no existen."""
    crear_tabla_usuarios = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK (rol IN ('empleado', 'jefe'))
    );
    """
    crear_tabla_tareas = """
    CREATE TABLE IF NOT EXISTS tareas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        fecha_entrega TEXT NOT NULL,
        prioridad INTEGER NOT NULL,
        tipo_tarea TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    );
    """
    try:
        cursor = conexion.cursor()
        cursor.execute(crear_tabla_usuarios)
        cursor.execute(crear_tabla_tareas)
        conexion.commit()
    except Error as e:
        print(f"Error al crear tablas: {e}")

def insertar_usuario(conexion, nombre, email, password, rol):
    """Método para insertar un nuevo usuario en la base de datos."""
    sql = '''INSERT INTO usuarios (nombre, email, password, rol)
             VALUES (?, ?, ?, ?);'''
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, (nombre, email, password, rol))
        conexion.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al insertar usuario: {e}")
        return None

def obtener_usuarios(conexion):
    """Método para obtener todos los usuarios de la base de datos."""
    sql = '''SELECT id, nombre, email, rol FROM usuarios;'''
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, email, rol FROM usuarios")
        usuarios = [{"id": row[0], "nombre": row[1], "email": row[2], "rol": row[3]} for row in cursor.fetchall()]
        return usuarios
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    
def obtener_tareas_de_usuario(conexion, usuario_id):
    """Método para obtener todas las tareas asignadas a un usuario específico."""
    sql = '''SELECT id, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea FROM tareas WHERE usuario_id = ? ORDER BY fecha_entrega, prioridad DESC;'''
    cursor = conexion.cursor()
    cursor.execute(sql, (usuario_id,))
    tareas = [{"id": row[0], "titulo": row[1], "descripcion": row[2], "fecha_entrega": row[3], "prioridad": row[4], "tipo_tarea": row[5]} for row in cursor.fetchall()]
    return tareas

def insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, usuario_id):
    """Método para insertar una nueva tarea en la base de datos."""
    sql = '''INSERT INTO tareas (titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, usuario_id)
             VALUES (?, ?, ?, ?, ?);'''
    cursor = conexion.cursor()
    cursor.execute(sql, (titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, usuario_id))
    conexion.commit()
    return cursor.lastrowid



if __name__ == '__main__':
    conexion = conectar_a_base_de_datos()
    crear_tablas(conexion)
    #insertar_usuario(conexion, 'juan', 'juan@gmail', 'juan', 'empleado')
    #insertar_usuario(conexion, 'Julián Ruiz', 'julian.ruiz@uclm.es', 'julian', 'jefe')
    usuarios = obtener_usuarios(conexion)
    for usuario in usuarios:
        print(usuario)
