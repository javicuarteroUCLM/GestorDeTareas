import tkinter as tk
from tkinter import messagebox
from tkinter import ttk,simpledialog, font
from tkcalendar import Calendar
import auth
import db


def mostrar_ventana_inicio_sesion():
    "Método para mostrar la ventana de inicio de sesión."
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

# Función para mostrar tareas en el calendario
def tareas_calendario(calendario, tasks):
    for task in tasks:
        date = task['fecha_entrega']
        title = task['titulo']
        # Crear evento en el calendario
        calendario.calevent_create(date, 'Tarea', title)
        # Configurar el color del evento
        calendario.calevent_tag_config('Tarea', background='red', foreground='white')


def mostrar_ventana_principal(usuario):
    "Método para mostrar la ventana principal"
    conexion = db.conectar_a_base_de_datos()
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Gestión de Tareas")

    fuente_bienvenida = font.Font(family="Helvetica", size=16, weight="bold")

    label_bienvenida = tk.Label(ventana_principal, text=f"Bienvenido {usuario['nombre']} - {usuario['rol']}", font=fuente_bienvenida)
    label_bienvenida.pack()

    marco_tareas = tk.Frame(ventana_principal)
    marco_tareas.pack()
    
    calendar_frame = tk.Frame(ventana_principal)
    calendar_frame.pack()

    calendario = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-mm-dd", font="Arial 14", locale="es_ES", disabledforeground="red", selectforeground="white", selectbackground="blue")
    calendario.pack()
    
    def mostrar_tareas_en_fecha_seleccionada():
        fecha_seleccionada = calendario.get_date()
        tareas_fecha_seleccionada = [tarea for tarea in db.obtener_tareas_de_usuario(conexion, usuario['id']) if tarea['fecha_entrega'] == fecha_seleccionada]

        texto_tareas = '\n'.join([f"{tarea['titulo']} - Prioridad: {tarea['prioridad']}" for tarea in tareas_fecha_seleccionada])
        messagebox.showinfo("Tareas para " + fecha_seleccionada, texto_tareas)

    tk.Button(ventana_principal, text="Mostrar eventos", command=mostrar_tareas_en_fecha_seleccionada).pack()
            
    def actualizar_lista_tareas(marco_tareas):
        for widget in marco_tareas.winfo_children():
            widget.destroy()
        tareas = db.obtener_tareas_de_usuario(conexion, usuario['id'])
        tareas_ordenadas = sorted(tareas, key=lambda x: (x['prioridad'], x['fecha_entrega']))
        for tarea in tareas_ordenadas:
            tk.Label(marco_tareas, text=f"{tarea['titulo']} - Fecha de entrega: {tarea['fecha_entrega']} - Prioridad: {tarea['prioridad']}").pack()


    actualizar_lista_tareas(marco_tareas)

    
    def agregar_tarea():
        ventana_agregar = tk.Toplevel(ventana_principal)
        ventana_agregar.title("Agregar Nueva Tarea")

        tk.Label(ventana_agregar, text="Título:").pack()
        titulo_entry = tk.Entry(ventana_agregar)
        titulo_entry.pack()

        tk.Label(ventana_agregar, text="Descripción:").pack()
        descripcion_entry = tk.Entry(ventana_agregar)
        descripcion_entry.pack()

        tk.Label(ventana_agregar, text="Fecha de entrega (YYYY-MM-DD):").pack()
        fecha_entrega_entry = tk.Entry(ventana_agregar)
        fecha_entrega_entry.pack()

        tk.Label(ventana_agregar, text="Prioridad (número):").pack()
        prioridad_entry = tk.Entry(ventana_agregar)
        prioridad_entry.pack()

        tk.Label(ventana_agregar, text="Tipo de tarea (trabajo, cotidiana u ocio):").pack()
        tipo_tarea_entry = tk.Entry(ventana_agregar)
        tipo_tarea_entry.pack()

        def confirmar_agregar():
            titulo = titulo_entry.get()
            descripcion = descripcion_entry.get()
            fecha_entrega = fecha_entrega_entry.get()
            prioridad = prioridad_entry.get()
            tipo_tarea = tipo_tarea_entry.get() 


            if titulo and fecha_entrega and prioridad and tipo_tarea:
                try:
                    prioridad = int(prioridad)  # Asegúrate de que la prioridad es un entero
                    db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, usuario['id'])
                    actualizar_lista_tareas(marco_tareas)  # Asegúrate de pasar el marco_tareas correcto
                    ventana_agregar.destroy()
                except ValueError:
                    messagebox.showwarning("Advertencia", "La prioridad debe ser un número.", parent=ventana_agregar)
            else:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.", parent=ventana_agregar)

        tk.Button(ventana_agregar, text="Agregar", command=confirmar_agregar).pack()


    #Botón para agregar tareas
    tk.Button(ventana_principal, text="Agregar Tarea", command=agregar_tarea).pack()

    #Bucle para cuando el rol del empleado sea jefe
    if usuario['rol'] == 'jefe':
        def asignar_tarea():
            asignar_ventana = tk.Toplevel(ventana_principal)
            asignar_ventana.title("Asignar Tarea a Empleado")

            # Obtenemos la lista de empleados para llenar el Combobox
            empleados = db.obtener_usuarios(conexion) 
            empleados_dict = {emp['nombre']: emp['id'] for emp in empleados if emp['rol'] == 'empleado'}

            tk.Label(asignar_ventana, text="Empleado:").pack()
            combo_empleados = ttk.Combobox(asignar_ventana, values=list(empleados_dict.keys()))
            combo_empleados.pack()

            tk.Label(asignar_ventana, text="Título:").pack()
            titulo_entry = tk.Entry(asignar_ventana)
            titulo_entry.pack()

            tk.Label(asignar_ventana, text="Descripción:").pack()
            descripcion_entry = tk.Text(asignar_ventana, height=3, width=40)
            descripcion_entry.pack()

            tk.Label(asignar_ventana, text="Fecha de entrega (YYYY-MM-DD):").pack()
            fecha_entrega_entry = tk.Entry(asignar_ventana)
            fecha_entrega_entry.pack()

            tk.Label(asignar_ventana, text="Prioridad (número):").pack()
            prioridad_entry = tk.Entry(asignar_ventana)
            prioridad_entry.pack()

            tipo_tarea_entry = 'trabajo'
            tipo_tarea_entry.pack()

            def confirmar_asignacion():
                empleado_seleccionado = combo_empleados.get()
                titulo = titulo_entry.get()
                descripcion = descripcion_entry.get("1.0", tk.END).strip()  # Obtenemos todo el texto desde la línea 1, columna 0 hasta el final
                fecha_entrega = fecha_entrega_entry.get()
                prioridad = prioridad_entry.get()
                tipo_tarea = tipo_tarea_entry.get()

                if empleado_seleccionado and titulo and fecha_entrega and prioridad:
                    try:
                        empleado_id = empleados_dict[empleado_seleccionado]
                        prioridad = int(prioridad)  # Convertimos la prioridad a entero
                        db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, empleado_id)
                        messagebox.showinfo("Éxito", "Tarea asignada correctamente.", parent=asignar_ventana)
                        asignar_ventana.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "La prioridad debe ser un número entero.", parent=asignar_ventana)
                else:
                    messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=asignar_ventana)

            tk.Button(asignar_ventana, text="Asignar Tarea", command=confirmar_asignacion).pack()

        tk.Button(ventana_principal, text="Asignar Tarea a Empleado", command=asignar_tarea).pack()

    ventana_principal.mainloop()

if __name__ == "__main__":
    mostrar_ventana_inicio_sesion()
