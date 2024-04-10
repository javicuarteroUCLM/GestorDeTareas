import tkinter as tk
from tkinter import messagebox
from tkinter import ttk,simpledialog
import auth
import db

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

    # Marco para las tareas
    marco_tareas = tk.Frame(ventana_principal)
    marco_tareas.pack()

    # Obtener y mostrar tareas
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
        else:
            messagebox.showwarning("Advertencia", "La tarea necesita al menos un título, fecha de entrega y prioridad.")


    # Botón para agregar tareas (visible para todos los usuarios)
    tk.Button(ventana_principal, text="Agregar Tarea", command=agregar_tarea).pack()

    # Si el usuario es jefe, añade la opción de asignar tareas a otros usuarios
    if usuario['rol'] == 'jefe':
        def asignar_tarea():
            asignar_ventana= tk.Toplevel(ventana_principal)
            asignar_ventana.title("Asignar Tarea a Empleado")

            tk.Label(asignar_ventana, text="Empleado:").pack()
            # Suponiendo que tienes una función en db.py que puede listar todos los empleados
            empleados = db.obtener_usuarios(conexion)  # Asegúrate de implementar esta función
            empleados_dict = {f"{emp['nombre']} ({emp['email']})": emp['id'] for emp in empleados if emp['rol'] == 'empleado'}
            combo_empleados = ttk.Combobox(asignar_ventana, values=list(empleados_dict.keys()))
            combo_empleados.pack()

            titulo = simpledialog.askstring("Título de la Tarea", "Ingrese el título de la tarea:", parent=asignar_ventana)
            descripcion = simpledialog.askstring("Descripción de la Tarea", "Ingrese la descripción de la tarea:", parent=asignar_ventana)
            fecha_entrega = simpledialog.askstring("Fecha de Entrega", "Ingrese la fecha de entrega (YYYY-MM-DD):", parent=asignar_ventana)
            prioridad = simpledialog.askinteger("Prioridad", "Ingrese la prioridad de la tarea (número):", parent=asignar_ventana)

            def confirmar_asignacion():
                empleado_seleccionado = combo_empleados.get()
                if empleado_seleccionado and titulo and fecha_entrega and prioridad is not None:
                    empleado_id = empleados_dict[empleado_seleccionado]
                    db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, empleado_id)
                    messagebox.showinfo("Éxito", "Tarea asignada correctamente.", parent=asignar_ventana)
                    asignar_ventana.destroy()
                else:
                    messagebox.showwarning("Advertencia", "Debe completar todos los campos.", parent=asignar_ventana)

            tk.Button(asignar_ventana, text="Asignar Tarea", command=confirmar_asignacion).pack()

        tk.Button(ventana_principal, text="Asignar Tarea a Empleado", command=asignar_tarea).pack()

    ventana_principal.mainloop()

if __name__ == "__main__":
    mostrar_ventana_inicio_sesion()
