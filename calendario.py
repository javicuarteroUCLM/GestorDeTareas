import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import auth
import db

# Función para mostrar tareas en el calendario
def tareas_calendario(calendario, tasks):
    for task in tasks:
        date = task['fecha_entrega']
        title = task['titulo']
        # Crear evento en el calendario
        calendario.calevent_create(date, 'Tarea', title)
        # Configurar el color del evento
        calendario.calevent_tag_config('Tarea', background='red', foreground='white')

# Ventana de inicio de sesión
def mostrar_ventana_inicio_sesion():
    ventana_inicio_sesion = tk.Tk()
    ventana_inicio_sesion.title("Inicio de Sesión")

    tk.Label(ventana_inicio_sesion, text="Email:").pack()
    email_entry = tk.Entry(ventana_inicio_sesion)
    email_entry.pack()

    tk.Label(ventana_inicio_sesion, text="Contraseña:").pack()
    password_entry = tk.Entry(ventana_inicio_sesion, show="*")
    password_entry.pack()

    def intento_inicio_sesion():
        usuario = auth.verificar_credenciales(email_entry.get(), password_entry.get())
        if usuario:
            ventana_inicio_sesion.destroy()
            mostrar_ventana_principal(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    tk.Button(ventana_inicio_sesion, text="Iniciar Sesión", command=intento_inicio_sesion).pack()
    ventana_inicio_sesion.mainloop()

# Ventana principal
def mostrar_ventana_principal(usuario):
    conexion = db.conectar_a_base_de_datos()
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Gestión de Tareas")

    tk.Label(ventana_principal, text=f"Bienvenido {usuario['nombre']} - {usuario['rol']}").pack()

    marco_tareas = tk.Frame(ventana_principal)
    marco_tareas.pack()

    calendar_frame = tk.Frame(ventana_principal)
    calendar_frame.pack()

    calendario = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd",
                                  font="Arial 14", locale="es_ES", disabledforeground="red",
                                  selectforeground="white", selectbackground="blue")
    calendario.pack()

    def actualizar_lista_tareas():
        marco_tareas = tk.Frame(ventana_principal)
        marco_tareas.pack()
        tareas = db.obtener_tareas_de_usuario(conexion, usuario['id'])
        for tarea in tareas:
            tk.Label(marco_tareas, text=f"{tarea['titulo']} - Fecha de entrega: {tarea['fecha_entrega']} - Prioridad: {tarea['prioridad']}").pack()

    actualizar_lista_tareas()

    # Función para agregar tareas
    def agregar_tarea():
        titulo = simpledialog.askstring("Agregar Tarea", "Título:")
        descripcion = simpledialog.askstring("Agregar Tarea", "Descripción:")
        fecha_entrega = simpledialog.askstring("Agregar Tarea", "Fecha de entrega (YYYY-MM-DD):")
        prioridad = simpledialog.askinteger("Agregar Tarea", "Prioridad (número):")
        if titulo and fecha_entrega and prioridad is not None:
            db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, usuario['id'])
            actualizar_lista_tareas()
            messagebox.showinfo("Éxito", "La tarea se ha añadido correctamente.")
            # Actualizar eventos en el calendario después de agregar una tarea
            actualizar_eventos_calendario(calendario, usuario, conexion)
        else:
            messagebox.showwarning("Advertencia", "La tarea necesita al menos un título, fecha de entrega y prioridad.")

    tk.Button(ventana_principal, text="Agregar Tarea", command=agregar_tarea).pack()
    tk.Button(ventana_principal, text="Mostrar eventos", command=actualizar_eventos_calendario).pack()

    ventana_principal.mainloop()

def actualizar_eventos_calendario(calendario, usuario, conexion):
    # Borra todos los eventos del calendario
    calendario.calevent_delete('all')

    # Obtener y mostrar tareas en el calendario
    tasks = db.obtener_tareas_de_usuario(conexion, usuario['id'])
    for task in tasks:
        date = task['fecha_entrega']
        title = task['titulo']
        # Crear evento en el calendario
        calendario.calevent_create(date, 'Tarea', title)
        # Configurar el color del evento
        calendario.calevent_tag_config('Tarea', background='red', foreground='white')

if __name__ == "__main__":
    mostrar_ventana_inicio_sesion()