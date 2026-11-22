import tkinter as matsi
from tkinter import ttk, messagebox
import CRUD


# Las operaciones de base de datos se encuentran en CRUD.py.

def crear_lista(padre, columnas, anchos=None, altura=12):
    marco = ttk.Frame(padre)
    marco.pack(fill="both", expand=True, padx=10, pady=10)
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=altura)
    for i, columna in enumerate(columnas):
        tabla.heading(columna, text=columna)
        tabla.column(columna, width=anchos[i] if anchos else 140, anchor="w")
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return tabla


def llenar_lista(tabla, filas):
    tabla.delete(*tabla.get_children())
    for fila in filas:
        tabla.insert("", "end", values=tuple("" if x is None else str(x) for x in fila))


def limpiar_pantalla():
    for elemento in contenido.winfo_children():
        elemento.destroy()


def volver_menu():
    limpiar_pantalla()
    mostrar_menu()


# -------------------------------------------------
# CALCULO AUTOMATICO DEL ESTADO DE UNA COMPUTADORA
# -------------------------------------------------

def calcular_estado(id_pc):
    componentes_pc = CRUD.obtener_estado_piezas_pc(id_pc)[0]
    perifericos_pc = CRUD.obtener_estado_piezas_pc(id_pc)[1]

    categorias_necesarias = [
        "Fuente_Alimentacion", "Microprocesador", "Motherboard",
        "Almacenamiento", "Memory_Ram", "Ventilacion"
    ]
    perifericos_necesarios = ["teclado", "mouse", "monitor"]

    categorias_presentes = [fila[0] for fila in componentes_pc]
    perifericos_presentes = [fila[0] for fila in perifericos_pc]

    completo = True
    for categoria in categorias_necesarias:
        if categoria not in categorias_presentes:
            completo = False

    for periferico in perifericos_necesarios:
        if periferico not in perifericos_presentes:
            completo = False

    for fila in componentes_pc + perifericos_pc:
        if fila[1] != "Buen_Estado":
            completo = False

    if completo:
        return "Buen_Estado"
    return "Mal_Estado"


# -------------------------------------------------
# PANTALLA PRINCIPAL
# -------------------------------------------------

def mostrar_menu():
    limpiar_pantalla()
    ttk.Label(contenido, text="TALLER DE HARDWARE", font=("Arial", 20, "bold")).pack(pady=35)
    ttk.Label(contenido, text="Seleccioná qué sección querés administrar.", font=("Arial", 11)).pack(pady=10)
    ttk.Label(contenido, text="Usá los botones superiores para cambiar de sección.", font=("Arial", 10)).pack(pady=8)


# -------------------------------------------------
# SECCION COMPUTADORAS
# -------------------------------------------------

def mostrar_computadoras():
    limpiar_pantalla()
    ttk.Label(contenido, text="Computadoras", font=("Arial", 16, "bold")).pack(pady=8)

    columnas = ("ID", "Nombre", "Fecha de armado", "Estado")
    global tabla_computadoras
    tabla_computadoras = crear_lista(contenido, columnas, (60, 180, 150, 130))

    filas = CRUD.obtener_computadoras()
    datos_lista = []
    for fila in filas:
        datos_lista.append((fila[0], fila[1], fila[2], calcular_estado(fila[0])))
    llenar_lista(tabla_computadoras, datos_lista)

    zona_botones = ttk.Frame(contenido)
    zona_botones.pack(fill="x", padx=10, pady=10)
    ttk.Button(zona_botones, text="Volver", command=volver_menu).pack(side="left")
    ttk.Button(zona_botones, text="Ver / Modificar", command=ver_computadora).pack(side="right", padx=5)
    ttk.Button(zona_botones, text="Desmontar", command=desmontar_computadora).pack(side="right", padx=5)
    ttk.Button(zona_botones, text="Nueva", command=nueva_computadora).pack(side="right", padx=5)


def obtener_pc_seleccionada():
    seleccion = tabla_computadoras.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "Tiene que seleccionar una PC")
        return None
    valores = tabla_computadoras.item(seleccion[0], "values")
    return int(valores[0])


def nueva_computadora():
    ventana_pc = matsi.Toplevel(ventana)
    ventana_pc.title("Nueva computadora")
    ventana_pc.geometry("360x220")
    ventana_pc.transient(ventana)
    ventana_pc.grab_set()

    ttk.Label(ventana_pc, text="Nombre de la computadora").pack(pady=(15, 3))
    entrada_nombre = ttk.Entry(ventana_pc, width=35)
    entrada_nombre.pack()

    ttk.Label(ventana_pc, text="Fecha de armado (AAAA-MM-DD)").pack(pady=(12, 3))
    entrada_fecha = ttk.Entry(ventana_pc, width=20)
    entrada_fecha.insert(0, "2026-01-01")
    entrada_fecha.pack()

    def guardar_pc():
        nombre = entrada_nombre.get().strip()
        fecha = entrada_fecha.get().strip()
        if not nombre or not fecha:
            messagebox.showwarning("Falta información", "Falta rellenar formulario")
            return
        if len(fecha) != 10 or fecha[4:5] != "-" or fecha[7:8] != "-":
            messagebox.showwarning("Fecha incorrecta", "Usá el formato AAAA-MM-DD")
            return
        try:
            id_nueva_pc = CRUD.crear_computadora(nombre, fecha)
            ventana_pc.destroy()
            mostrar_computadoras()
            abrir_detalle_computadora(id_nueva_pc)
        except Exception as e:
            messagebox.showerror("Error", "No se pudo crear la computadora.\n" + str(e))

    ttk.Button(ventana_pc, text="Guardar y asignar piezas", command=guardar_pc).pack(pady=18)


def ver_computadora():
    id_pc = obtener_pc_seleccionada()
    if id_pc is not None:
        abrir_detalle_computadora(id_pc)


def abrir_detalle_computadora(id_pc):
    datos_pc = CRUD.obtener_computadora(id_pc)
    if not datos_pc:
        return
    nombre, fecha = datos_pc[0]
    limpiar_pantalla()

    ttk.Label(contenido, text="Computadora: " + nombre, font=("Arial", 16, "bold")).pack(pady=5)
    ttk.Label(contenido, text="Fecha de armado: " + str(fecha) + "    Estado: " + calcular_estado(id_pc)).pack(pady=3)

    marco_componentes = ttk.LabelFrame(contenido, text="Componentes instalados")
    marco_componentes.pack(fill="both", expand=True, padx=10, pady=5)
    global tabla_detalle_componentes
    tabla_detalle_componentes = crear_lista(marco_componentes,
        ("ID", "Categoría", "Marca", "Nombre técnico", "Estado"), (50, 145, 120, 190, 110), 5)
    llenar_lista(tabla_detalle_componentes, CRUD.obtener_componentes_pc(id_pc))

    botones_componentes = ttk.Frame(contenido)
    botones_componentes.pack(fill="x", padx=10)
    ttk.Button(botones_componentes, text="Agregar / Cambiar componente", command=lambda: seleccionar_componente(id_pc)).pack(side="left")
    ttk.Button(botones_componentes, text="Quitar componente", command=lambda: quitar_componente(id_pc)).pack(side="left", padx=5)

    marco_perifericos = ttk.LabelFrame(contenido, text="Periféricos instalados")
    marco_perifericos.pack(fill="both", expand=True, padx=10, pady=5)
    global tabla_detalle_perifericos
    tabla_detalle_perifericos = crear_lista(marco_perifericos,
        ("ID", "Nombre", "Marca", "Estado"), (50, 140, 160, 110), 3)
    llenar_lista(tabla_detalle_perifericos, CRUD.obtener_perifericos_pc(id_pc))

    botones_perifericos = ttk.Frame(contenido)
    botones_perifericos.pack(fill="x", padx=10)
    ttk.Button(botones_perifericos, text="Agregar / Cambiar periférico", command=lambda: seleccionar_periferico(id_pc)).pack(side="left")
    ttk.Button(botones_perifericos, text="Quitar periférico", command=lambda: quitar_periferico(id_pc)).pack(side="left", padx=5)

    ttk.Button(contenido, text="Volver a computadoras", command=mostrar_computadoras).pack(pady=8)


def seleccionar_componente(id_pc):
    categorias = ["Fuente_Alimentacion", "Microprocesador", "Motherboard", "Almacenamiento", "Memory_Ram", "Ventilacion"]
    ventana_sel = matsi.Toplevel(ventana)
    ventana_sel.title("Seleccionar componente de caja")
    ventana_sel.geometry("760x390")
    ventana_sel.transient(ventana)
    ventana_sel.grab_set()

    ttk.Label(ventana_sel, text="Categoría").pack(pady=(10, 2))
    categoria = matsi.StringVar(value=categorias[0])
    combo = ttk.Combobox(ventana_sel, textvariable=categoria, values=categorias, state="readonly", width=28)
    combo.pack()
    tabla = crear_lista(ventana_sel, ("ID", "Categoría", "Marca", "Nombre técnico", "Estado"), (50, 150, 130, 220, 110), 9)

    def cargar_disponibles(event=None):
        filas = CRUD.obtener_componentes_disponibles(categoria.get())
        llenar_lista(tabla, filas)
    combo.bind("<<ComboboxSelected>>", cargar_disponibles)
    cargar_disponibles()

    def asignar():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Tiene que seleccionar un componente")
            return
        id_comp = int(tabla.item(sel[0], "values")[0])
        cat = categoria.get()
        cantidad = CRUD.contar_componentes_categoria(id_pc, cat)
        limite = 4 if cat == "Memory_Ram" else 2 if cat == "Almacenamiento" else 1
        if cantidad >= limite:
            messagebox.showwarning("Límite alcanzado", "Esta computadora ya tiene el máximo permitido para esa categoría.")
            return
        if cat not in ("Memory_Ram", "Almacenamiento") and cantidad == 1:
            messagebox.showwarning("Componente existente", "Primero quitá el componente actual de esta categoría.")
            return
        if CRUD.asignar_componente(id_pc, id_comp):
            ventana_sel.destroy()
            abrir_detalle_computadora(id_pc)

    ttk.Button(ventana_sel, text="Asignar", command=asignar).pack(pady=10)


def seleccionar_periferico(id_pc):
    nombres = ["teclado", "mouse", "monitor"]
    ventana_sel = matsi.Toplevel(ventana)
    ventana_sel.title("Seleccionar periférico de caja")
    ventana_sel.geometry("650x360")
    ventana_sel.transient(ventana)
    ventana_sel.grab_set()

    ttk.Label(ventana_sel, text="Tipo de periférico").pack(pady=(10, 2))
    tipo = matsi.StringVar(value=nombres[0])
    combo = ttk.Combobox(ventana_sel, textvariable=tipo, values=nombres, state="readonly", width=20)
    combo.pack()
    tabla = crear_lista(ventana_sel, ("ID", "Nombre", "Marca", "Estado"), (55, 130, 170, 120), 8)

    def cargar_disponibles(event=None):
        filas = CRUD.obtener_perifericos_disponibles(tipo.get())
        llenar_lista(tabla, filas)
    combo.bind("<<ComboboxSelected>>", cargar_disponibles)
    cargar_disponibles()

    def asignar():
        sel = tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Tiene que seleccionar un periférico")
            return
        id_per = int(tabla.item(sel[0], "values")[0])
        cantidad = CRUD.contar_perifericos_tipo(id_pc, tipo.get())
        if cantidad >= 1:
            messagebox.showwarning("Periférico existente", "Esta computadora ya tiene ese periférico. Primero quitá el actual.")
            return
        if CRUD.asignar_periferico(id_pc, id_per):
            ventana_sel.destroy()
            abrir_detalle_computadora(id_pc)

    ttk.Button(ventana_sel, text="Asignar", command=asignar).pack(pady=10)


def quitar_componente(id_pc):
    sel = tabla_detalle_componentes.selection()
    if not sel:
        messagebox.showwarning("Atención", "Tiene que seleccionar un componente")
        return
    id_comp = int(tabla_detalle_componentes.item(sel[0], "values")[0])
    if messagebox.askyesno("Confirmar", "¿Querés devolver este componente a la caja?"):
        if CRUD.devolver_componente_a_caja(id_comp):
            abrir_detalle_computadora(id_pc)


def quitar_periferico(id_pc):
    sel = tabla_detalle_perifericos.selection()
    if not sel:
        messagebox.showwarning("Atención", "Tiene que seleccionar un periférico")
        return
    id_per = int(tabla_detalle_perifericos.item(sel[0], "values")[0])
    if messagebox.askyesno("Confirmar", "¿Querés devolver este periférico a la caja?"):
        if CRUD.devolver_periferico_a_caja(id_per):
            abrir_detalle_computadora(id_pc)


def desmontar_computadora():
    id_pc = obtener_pc_seleccionada()
    if id_pc is None:
        return
    if messagebox.askyesno("Desmontar computadora", "¿Querés desmontar esta PC? Sus componentes y periféricos volverán a la caja."):
        if CRUD.eliminar_computadora(id_pc):
            mostrar_computadoras()


# -------------------------------------------------
# -------------------------------------------------
# SECCION COMPONENTES
# -------------------------------------------------

def mostrar_componentes():
    limpiar_pantalla()
    ttk.Label(contenido, text="Inventario de componentes", font=("Arial", 16, "bold")).pack(pady=8)

    global ubicacion_componentes, filtro_categoria, filtro_estado, tabla_componentes
    ubicacion_componentes = matsi.StringVar(value="En caja")
    filtro_categoria = matsi.StringVar(value="Todas")
    filtro_estado = matsi.StringVar(value="Todos")

    zona_filtros = ttk.Frame(contenido)
    zona_filtros.pack(fill="x", padx=10, pady=5)

    ttk.Label(zona_filtros, text="Ubicación:").pack(side="left", padx=(0, 4))
    combo_ubicacion = ttk.Combobox(zona_filtros, textvariable=ubicacion_componentes,
        values=("En caja", "En PC"), state="readonly", width=12)
    combo_ubicacion.pack(side="left", padx=4)

    ttk.Label(zona_filtros, text="Categoría:").pack(side="left", padx=(12, 4))
    combo_categoria = ttk.Combobox(zona_filtros, textvariable=filtro_categoria,
        values=("Todas", "Fuente_Alimentacion", "Microprocesador", "Motherboard",
                "Almacenamiento", "Memory_Ram", "Ventilacion"),
        state="readonly", width=22)
    combo_categoria.pack(side="left", padx=4)

    ttk.Label(zona_filtros, text="Estado:").pack(side="left", padx=(12, 4))
    combo_estado = ttk.Combobox(zona_filtros, textvariable=filtro_estado,
        values=("Todos", "Buen_Estado", "Mal_Estado"), state="readonly", width=15)
    combo_estado.pack(side="left", padx=4)

    columnas = ("ID", "Ubicación", "Categoría", "Marca", "Nombre técnico", "Estado")
    tabla_componentes = crear_lista(contenido, columnas, (55, 120, 155, 120, 190, 120), 14)

    zona_botones = ttk.Frame(contenido)
    zona_botones.pack(fill="x", padx=10, pady=10)
    ttk.Button(zona_botones, text="Volver", command=volver_menu).pack(side="left")
    ttk.Button(zona_botones, text="Nuevo", command=lambda: formulario_componente()).pack(side="right", padx=4)
    ttk.Button(zona_botones, text="Modificar", command=modificar_componente_seleccionado).pack(side="right", padx=4)
    ttk.Button(zona_botones, text="Eliminar", command=eliminar_componente_seleccionado).pack(side="right", padx=4)

    combo_ubicacion.bind("<<ComboboxSelected>>", cargar_componentes)
    combo_categoria.bind("<<ComboboxSelected>>", cargar_componentes)
    combo_estado.bind("<<ComboboxSelected>>", cargar_componentes)
    cargar_componentes()


def cargar_componentes(event=None):
    filas = CRUD.obtener_componentes_filtrados(
        ubicacion_componentes.get(), filtro_categoria.get(), filtro_estado.get()
    )
    llenar_lista(tabla_componentes, filas)


def obtener_componente_seleccionado():
    seleccion = tabla_componentes.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "Tiene que seleccionar un componente")
        return None
    return int(tabla_componentes.item(seleccion[0], "values")[0])


def formulario_componente(id_componente=None):
    es_edicion = id_componente is not None
    ventana_form = matsi.Toplevel(ventana)
    ventana_form.title("Modificar componente" if es_edicion else "Nuevo componente")
    ventana_form.geometry("420x390")
    ventana_form.transient(ventana)
    ventana_form.grab_set()

    categorias = ("Fuente_Alimentacion", "Microprocesador", "Motherboard",
                  "Almacenamiento", "Memory_Ram", "Ventilacion")
    estados = ("Buen_Estado", "Mal_Estado")

    ttk.Label(ventana_form, text="Categoría").pack(pady=(12, 3))
    entrada_categoria = ttk.Combobox(ventana_form, values=categorias, state="readonly", width=30)
    entrada_categoria.pack()

    ttk.Label(ventana_form, text="Marca").pack(pady=(9, 3))
    entrada_marca = ttk.Entry(ventana_form, width=34)
    entrada_marca.pack()

    ttk.Label(ventana_form, text="Nombre técnico").pack(pady=(9, 3))
    entrada_nombre = ttk.Entry(ventana_form, width=34)
    entrada_nombre.pack()

    ttk.Label(ventana_form, text="Estado").pack(pady=(9, 3))
    entrada_estado = ttk.Combobox(ventana_form, values=estados, state="readonly", width=30)
    entrada_estado.pack()

    ttk.Label(ventana_form, text="Ubicación en caja").pack(pady=(9, 3))
    entrada_ubicacion = ttk.Entry(ventana_form, width=34)
    entrada_ubicacion.pack()

    if es_edicion:
        datos = CRUD.obtener_componente(id_componente)
        if not datos:
            messagebox.showerror("Error", "No se encontró el componente.")
            ventana_form.destroy()
            return
        categoria, marca, nombre, estado, ubicacion = datos[0]
        entrada_categoria.set(categoria)
        entrada_marca.insert(0, marca)
        entrada_nombre.insert(0, nombre)
        entrada_estado.set(estado)
        entrada_ubicacion.insert(0, ubicacion or "")
    else:
        entrada_categoria.set(categorias[0])
        entrada_estado.set("Buen_Estado")

    def guardar():
        categoria = entrada_categoria.get()
        marca = entrada_marca.get().strip()
        nombre = entrada_nombre.get().strip()
        estado = entrada_estado.get()
        ubicacion = entrada_ubicacion.get().strip()

        if not categoria or not marca or not nombre or not estado:
            messagebox.showwarning("Falta información", "Falta rellenar formulario")
            return

        try:
            if es_edicion:
                CRUD.modificar_componente(id_componente, categoria, marca, nombre, estado, ubicacion or None)
            else:
                CRUD.crear_componente(categoria, marca, nombre, estado, ubicacion or None)
            ventana_form.destroy()
            cargar_componentes()
        except Exception as e:
            messagebox.showerror("Error", "No se pudo guardar el componente.\\n" + str(e))

    ttk.Button(ventana_form, text="Guardar", command=guardar).pack(pady=18)


def modificar_componente_seleccionado():
    id_componente = obtener_componente_seleccionado()
    if id_componente is None:
        return
    valores = tabla_componentes.item(tabla_componentes.selection()[0], "values")
    if valores[1] != "En caja":
        messagebox.showwarning("No se puede modificar",
            "Para modificar un componente, primero debe estar en caja.")
        return
    formulario_componente(id_componente)


def eliminar_componente_seleccionado():
    id_componente = obtener_componente_seleccionado()
    if id_componente is None:
        return
    valores = tabla_componentes.item(tabla_componentes.selection()[0], "values")
    if valores[1] != "En caja":
        messagebox.showwarning("No se puede eliminar",
            "Para eliminar un componente instalado, primero hay que quitarlo de la PC.")
        return
    if messagebox.askyesno("Confirmar eliminación", "¿Está seguro de eliminar este componente?"):
        try:
            CRUD.eliminar_componente(id_componente)
            cargar_componentes()
        except Exception as e:
            messagebox.showerror("Error", "No se pudo eliminar el componente.\\n" + str(e))


# SECCION PERIFERICOS (SE COMPLETARA EN LA SIGUIENTE ETAPA)
# -------------------------------------------------

def mostrar_perifericos():
    limpiar_pantalla()
    ttk.Label(contenido, text="Periféricos", font=("Arial", 16, "bold")).pack(pady=8)
    columnas = ("ID", "Ubicación", "Nombre", "Marca", "Estado")
    tabla = crear_lista(contenido, columnas, (55, 120, 130, 160, 120))
    filas = CRUD.obtener_inventario_perifericos()
    llenar_lista(tabla, filas)
    zona = ttk.Frame(contenido)
    zona.pack(fill="x", padx=10, pady=10)
    ttk.Button(zona, text="Volver", command=volver_menu).pack(side="left")
    ttk.Label(zona, text="La administración de periféricos se completará en la próxima etapa.").pack(side="right")


# -------------------------------------------------
# CREACION DE LA VENTANA
# -------------------------------------------------

ventana = matsi.Tk()
ventana.title("Taller de Hardware")
ventana.geometry("1000x700")
ventana.minsize(800, 600)

barra_principal = ttk.Frame(ventana)
barra_principal.pack(fill="x", padx=10, pady=10)

ttk.Button(barra_principal, text="Computadoras", command=mostrar_computadoras).pack(side="left", expand=True, fill="x", padx=4)
ttk.Button(barra_principal, text="Componentes", command=mostrar_componentes).pack(side="left", expand=True, fill="x", padx=4)
ttk.Button(barra_principal, text="Periféricos", command=mostrar_perifericos).pack(side="left", expand=True, fill="x", padx=4)

contenido = ttk.Frame(ventana)
contenido.pack(fill="both", expand=True)
mostrar_menu()
ventana.mainloop()
