import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, font
from tkcalendar import Calendar
import auth
import db
import datetime



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
        "Método para comprobar las credenciales introducidas por el usuario."
        usuario = auth.verificar_credenciales(email_entry.get(), password_entry.get())
        if usuario:
            ventana_inicio_sesion.destroy()
            mostrar_ventana_principal(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    tk.Button(ventana_inicio_sesion, text="Iniciar Sesión", command=intento_inicio_sesion).pack()
    ventana_inicio_sesion.mainloop()
        
def marcar_dias_con_tareas(calendario, tareas):
    "Método para marcar en azul clarito los días en los que hay tareas en el calendario."
    fechas_con_tareas = set()
    for tarea in tareas:
        try:
            fecha_obj = datetime.datetime.strptime(tarea['fecha_entrega'], '%d-%m-%Y').date()
            fechas_con_tareas.add(fecha_obj)
        except ValueError as e:
            print(f"Error al convertir la fecha: {e}")

    for fecha in fechas_con_tareas:
        calendario.calevent_create(fecha, 'Tarea', 'tarea')
        calendario.tag_config('tarea', background='lightblue') #Ponemos el color en de fondo en azul clarito
        
def actualizar_eventos_calendario(calendario, tareas):
    "Método para actualizar los eventos del calendario, para por ejemplo cuando se elimina una tarea."
    calendario.calevent_remove('all')
    marcar_dias_con_tareas(calendario, tareas)

def mostrar_ventana_principal(usuario):
    "Método para mostrar la ventana principal"
    conexion = db.conectar_a_base_de_datos()
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Gestión de Tareas")

    fuente_bienvenida = font.Font(family="Helvetica", size=16, weight="bold")

    label_bienvenida = tk.Label(ventana_principal, text=f"¡Bienvenido {usuario['nombre']} - {usuario['rol']}!", font=fuente_bienvenida)
    label_bienvenida.pack()
    
    def cerrar_sesion():
        "Método para cerrar sesión"
        if messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres cerrar sesión?"):
            ventana_principal.destroy()
            mostrar_ventana_inicio_sesion()
            
    #Botón para cerrar sesión
    boton_cerrar_sesion = tk.Button(ventana_principal, text="Cerrar sesión", bg="red", fg="white", command=cerrar_sesion)
    boton_cerrar_sesion.pack(anchor='ne', padx=10, pady=5)  
    
    calendar_frame = tk.Frame(ventana_principal)
    calendar_frame.pack()

    calendario = Calendar(calendar_frame, selectmode="day", date_pattern="dd-mm-yyyy", font="Arial 14", locale="es_ES", disabledforeground="red", selectforeground="white", selectbackground="blue")
    calendario.pack()

    
    marco_tareas = tk.Frame(ventana_principal)
    marco_tareas.pack(fill='both', expand=True)
    
    fuente_titulos_tareas = font.Font(family="Helvetica", size=12, weight="bold")
    
    def mostrar_tareas_en_fecha_seleccionada():
        "Método para mostrar las tareas que hay en un día específico. "
        fecha_seleccionada = calendario.get_date()
        tareas_fecha_seleccionada = [tarea for tarea in db.obtener_tareas_de_usuario(conexion, usuario['id']) if tarea['fecha_entrega'] == fecha_seleccionada]

        texto_tareas = '\n'.join([f"{tarea['titulo']} - Prioridad: {tarea['prioridad']}" for tarea in tareas_fecha_seleccionada])
        messagebox.showinfo("Tareas para " + fecha_seleccionada, texto_tareas)
        

    tk.Button(ventana_principal, text="Mostrar tareas", command=mostrar_tareas_en_fecha_seleccionada).pack()
            
    def actualizar_lista_tareas(marco_tareas, usuario_id):
        "Método para actualizar la lista de tareas en la interfaz gráfica."
        for widget in marco_tareas.winfo_children():  # Primero limpiamos los marcos de tareas existentes
            widget.destroy()

        tareas = db.obtener_tareas_de_usuario(conexion, usuario_id)
        tareas = sorted(tareas, key=lambda x: (x['prioridad'], x['fecha_entrega']))

        marcar_dias_con_tareas(calendario, tareas)

        marco_trabajo = tk.LabelFrame(marco_tareas, text='TRABAJO', labelanchor='n', font=fuente_titulos_tareas)
        marco_trabajo.pack(side='left', fill='both', expand=True,padx=5)
        
        marco_ocio = tk.LabelFrame(marco_tareas, text='OCIO', labelanchor='n', font=fuente_titulos_tareas)
        marco_ocio.pack(side='left', fill='both', expand=True,padx=5)
        
        marco_cotidiana = tk.LabelFrame(marco_tareas, text='COTIDIANA', labelanchor='n',font=fuente_titulos_tareas)
        marco_cotidiana.pack(side='left', fill='both', expand=True,padx=5)
        
        def click_tarea(tarea_id, event):
            "Método para mostrar un mini menú cuando pulsamos sobre alguna tarea."
            popup_menu = tk.Menu(marco_tareas, tearoff=0)
            popup_menu.add_command(label="Editar", command=lambda: editar_tarea(tarea_id))
            popup_menu.add_command(label="Eliminar", command=lambda: eliminar_tarea(tarea_id))
            popup_menu.add_command(label="Marcar como hecha", command=lambda: marcar_como_hecha(tarea_id))

            popup_menu.tk_popup(event.x_root, event.y_root) # Esto nos muestra el menú en la posición del clic

        def agregar_tareas_a_marco(marco, tareas):
            "Método para agregar las tareas a la columna según el tipo de tarea."
            for tarea in tareas:
                tarea_label = tk.Label(marco, text=f"{tarea['titulo']} - Fecha de entrega: {tarea['fecha_entrega']} - Prioridad: {tarea['prioridad']}")
                tarea_label.pack()
                tarea_label.bind("<Button-1>", lambda event, tarea_id=tarea['id']: click_tarea(tarea_id, event)) # Para asociar el evento de clic del botón izquierdo del ratoón a la etiqueta de tarea
                
                
        agregar_tareas_a_marco(marco_trabajo, [t for t in tareas if t['tipo_tarea'] == 'TRABAJO'])
        agregar_tareas_a_marco(marco_ocio, [t for t in tareas if t['tipo_tarea'] == 'OCIO'])
        agregar_tareas_a_marco(marco_cotidiana, [t for t in tareas if t['tipo_tarea'] == 'COTIDIANA'])

        def editar_tarea(tarea_id):
            "Método para editar una tarea."
            
            tarea = db.obtener_tarea_por_id(conexion, tarea_id)

            ventana_editar = tk.Toplevel(ventana_principal) #Creamos la ventana editar tarea
            ventana_editar.title("Editar Tarea")

            tk.Label(ventana_editar, text="Título:").pack()
            titulo_entry = tk.Entry(ventana_editar)
            titulo_entry.insert(0, tarea['titulo'])
            titulo_entry.pack()

            tk.Label(ventana_editar, text="Descripción:").pack()
            descripcion_entry = tk.Text(ventana_editar, height=3, width=40)
            descripcion_entry.insert('1.0', tarea['descripcion'])
            descripcion_entry.pack()

            tk.Label(ventana_editar, text="Fecha de entrega (dd-mm-aaaa):").pack()
            fecha_entrega_entry = tk.Entry(ventana_editar)
            fecha_entrega_entry.insert(0, tarea['fecha_entrega'])
            fecha_entrega_entry.pack()

            tk.Label(ventana_editar, text="Prioridad (número):").pack()
            prioridad_entry = tk.Entry(ventana_editar)
            prioridad_entry.insert(0, str(tarea['prioridad']))
            prioridad_entry.pack()

            tk.Label(ventana_editar, text="Tipo de tarea (trabajo, cotidiana u ocio):").pack()
            tipo_tarea_entry = tk.Entry(ventana_editar)
            tipo_tarea_entry.insert(0, tarea['tipo_tarea'])
            tipo_tarea_entry.pack()

            def confirmar_edicion():
                "Método confirmar la escritura de los nuevos datos"
                db.actualizar_tarea(conexion, tarea_id, titulo_entry.get(), descripcion_entry.get("1.0", tk.END), fecha_entrega_entry.get(), prioridad_entry.get(), tipo_tarea_entry.get())
                ventana_editar.destroy() #Cierra la ventana
                actualizar_lista_tareas(marco_tareas, usuario_id)
                actualizar_eventos_calendario(calendario, db.obtener_tareas_de_usuario(conexion, usuario_id))

            tk.Button(ventana_editar, text="Confirmar", command=confirmar_edicion).pack()

        def eliminar_tarea(tarea_id):
            "Mñetodo para eliminar una tarea."
            db.eliminar_tarea(conexion, tarea_id)
            tareas_actualizadas = db.obtener_tareas_de_usuario(conexion, usuario_id)
            actualizar_eventos_calendario(calendario, tareas_actualizadas)
            actualizar_lista_tareas(marco_tareas, usuario_id)

        def marcar_como_hecha(tarea_id):
            "Método para marcar una tarea como hecha."
            db.marcar_tarea_como_hecha(conexion, tarea_id)
            tareas_actualizadas = db.obtener_tareas_de_usuario(conexion, usuario_id)
            actualizar_eventos_calendario(calendario, tareas_actualizadas)
            actualizar_lista_tareas(marco_tareas, usuario_id)


    actualizar_lista_tareas(marco_tareas,usuario['id'])

    
    def agregar_tarea():
        "Método para agregar una nuwva tarea."
        fecha_seleccionada = calendario.get_date()
        
        ventana_agregar = tk.Toplevel(ventana_principal)
        ventana_agregar.title("Agregar Nueva Tarea")

        tk.Label(ventana_agregar, text="Título:").pack()
        titulo_entry = tk.Entry(ventana_agregar)
        titulo_entry.pack()

        tk.Label(ventana_agregar, text="Descripción:").pack()
        descripcion_entry = tk.Entry(ventana_agregar)
        descripcion_entry.pack()

        tk.Label(ventana_agregar, text="Fecha de entrega (DD-MM-AAAA):").pack()
        fecha_entrega_entry = tk.Entry(ventana_agregar)
        fecha_entrega_entry.pack()

        tk.Label(ventana_agregar, text="Prioridad (número):").pack()
        prioridad_entry = tk.Entry(ventana_agregar)
        fecha_entrega_entry.insert(0, fecha_seleccionada)
        prioridad_entry.pack()

        tk.Label(ventana_agregar, text="Tipo de tarea:").pack()
        tipo_tarea_combobox = ttk.Combobox(ventana_agregar, values=["TRABAJO", "COTIDIANA", "OCIO"])
        tipo_tarea_combobox.pack()

        def confirmar_agregar():
            "Confirma la escritura de los datos de la nueva tarea."
            titulo = titulo_entry.get()
            descripcion = descripcion_entry.get()
            fecha_entrega = fecha_entrega_entry.get()
            prioridad = prioridad_entry.get()
            tipo_tarea = tipo_tarea_combobox.get() 


            if titulo and fecha_entrega and prioridad and tipo_tarea:
                try:
                    "Bucle para comprobar los datos"
                    prioridad = int(prioridad) 
                    db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, usuario['id'])
                    actualizar_lista_tareas(marco_tareas,usuario['id'])
                    ventana_agregar.destroy()
                except ValueError:
                    messagebox.showwarning("Advertencia", "La prioridad debe ser un número.", parent=ventana_agregar)
            else:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.", parent=ventana_agregar)

        tk.Button(ventana_agregar, text="Agregar", command=confirmar_agregar).pack()

    tk.Button(ventana_principal, text="Agregar Tarea", command=agregar_tarea).pack() #Botón para agregar tareas

    if usuario['rol'] == 'jefe':
        "Comprobación de si el usuario es jefe o no."
        def asignar_tarea():
            "Método para asignar una tarea a un empleado."
            asignar_ventana = tk.Toplevel(ventana_principal)
            asignar_ventana.title("Asignar Tarea a Empleado")

            empleados = db.obtener_usuarios(conexion) #Obtenemos los usuarios 
            empleados_dict = {emp['nombre']: emp['id'] for emp in empleados if emp['rol'] == 'empleado'} #Creamos un diccionario con los empleados

            tk.Label(asignar_ventana, text="Empleado:").pack()
            combo_empleados = ttk.Combobox(asignar_ventana, values=list(empleados_dict.keys()))
            combo_empleados.pack()

            tk.Label(asignar_ventana, text="Título:").pack()
            titulo_entry = tk.Entry(asignar_ventana)
            titulo_entry.pack()

            tk.Label(asignar_ventana, text="Descripción:").pack()
            descripcion_entry = tk.Text(asignar_ventana, height=3, width=40)
            descripcion_entry.pack()

            tk.Label(asignar_ventana, text="Fecha de entrega (dd-mm-aaaa):").pack()
            fecha_entrega_entry = tk.Entry(asignar_ventana)
            fecha_entrega_entry.pack()

            tk.Label(asignar_ventana, text="Prioridad (número):").pack()
            prioridad_entry = tk.Entry(asignar_ventana)
            prioridad_entry.pack()
            
            tk.Label(asignar_ventana, text="Tipo de tarea (trabajo, cotidiana u ocio):").pack()
            tipo_tarea_entry = tk.Entry(asignar_ventana)
            tipo_tarea_entry.insert(0, "TRABAJO")  #Establecemos TRABAJO como valor por defecto
            tipo_tarea_entry.config(state='readonly') #Para que no lo pueda cambiar, es decir, que solo pueda asignar tareas de tipo TRABAJO
            tipo_tarea_entry.pack()

            def confirmar_asignacion():
                "Método para confirmar la asignación de la tarea."
                empleado_seleccionado = combo_empleados.get()
                titulo = titulo_entry.get()
                descripcion = descripcion_entry.get("1.0", tk.END).strip()  #Obtenemos todo el texto desde la línea 1, columna 0 hasta el final
                fecha_entrega = fecha_entrega_entry.get()
                prioridad = prioridad_entry.get()
                tipo_tarea = tipo_tarea_entry.get()

                if empleado_seleccionado and titulo and fecha_entrega and prioridad:
                    try:
                        "Bucle para comprobar los datos."
                        empleado_id = empleados_dict[empleado_seleccionado]
                        prioridad = int(prioridad) 
                        db.insertar_tarea(conexion, titulo, descripcion, fecha_entrega, prioridad, tipo_tarea, empleado_id)
                        messagebox.showinfo("Éxito", "Tarea asignada correctamente.", parent=asignar_ventana)
                        asignar_ventana.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "La prioridad debe ser un número entero.", parent=asignar_ventana)
                else:
                    messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=asignar_ventana)

            tk.Button(asignar_ventana, text="Asignar Tarea", command=confirmar_asignacion).pack()

        tk.Button(ventana_principal, text="Asignar Tarea a Empleado", command=asignar_tarea).pack()

    ventana_principal.mainloop() #Bucle principal de la ventana principal

if __name__ == "__main__":
    mostrar_ventana_inicio_sesion()