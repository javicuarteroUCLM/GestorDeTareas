import sqlite3

def conectar_a_base_de_datos(db_path='sistema_tareas.db'):
    """Método para conectarse a la base de datos SQLite y devuelve la conexión."""
    try:
        conexion = sqlite3.connect(db_path)
        return conexion
    except sqlite3.Error as error:
        print(f"Error al conectar a la base de datos SQLite: {error}")
        return None

def verificar_credenciales(email, password):
    """Método para verificar si las credenciales coinciden con algún usuario en la base de datos."""
    conexion = conectar_a_base_de_datos()
    if conexion:
        cursor = conexion.cursor()
        consulta = "SELECT id, nombre, rol FROM usuarios WHERE email = ? AND password = ?"
        cursor.execute(consulta, (email, password))
        usuario = cursor.fetchone()
        conexion.close()
        if usuario:
            return {"id": usuario[0], "nombre": usuario[1], "rol": usuario[2]}
        else:
            return None
    else:
        return None

