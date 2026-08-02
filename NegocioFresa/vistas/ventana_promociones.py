import tkinter as tk
from tkinter import ttk, messagebox
from logica.promociones import (
    obtener_todas_promociones, 
    agregar_promocion, 
    actualizar_promocion, 
    cambiar_estado_promocion_bd
)
from logica.inventario import listar_producto

def actualizar_grilla_promociones(tree):
    """
    Limpia y recarga la lista de promociones en el Treeview
    """
    for item in tree.get_children():
        tree.delete(item)

    for p in obtener_todas_promociones():
        texto_estado = "Alta" if p['estado'] == 1 else "Inactiva"
        tree.insert("", tk.END, values=(
            p['id'],
            p['nombre_promo'],
            p['id_producto'],
            p['descripcion_producto'],
            p['cantidad_requerida'],
            f"${p['precio_promo']:.2f}",
            texto_estado
        ))

def cargar_datos_para_edicion_promo(event, tree, entries, combos):
    """
    Captura el doble clic en la grilla y sube los datos al formulario.
    NOTA: Al editar, bloqueamos el nombre y producto para que no se hagan líos,
    solo permitimos actualizar la cantidad y el precio.
    """
    seleccion = tree.selection()
    if not seleccion:
        return

    item = tree.item(seleccion[0])
    valores = item['values'] # Obtenemos los datos de la promo

    # 1. Habilitamos temporalmente los campos bloqueados para llenarlos
    entries['id'].config(state='normal')
    entries['nombre'].config(state='normal')
    combos['producto'].config(state='normal')

    # 2. Limpiamos los campos
    for e in entries.values():
        e.delete(0, tk.END)
    
    # 3. Cargamos los datos crudos
    entries['id'].insert(0, valores[0])
    entries['nombre'].insert(0, valores[1])
    
    # Buscamos el índice del producto en el combobox para setearlo
    # El valor[3] es la descripcion, pero para ser más seguros usamos el ID (valor[2])
    try:
        idx_prod = combos['prod_ids'].index(str(valores[2]))
        combos['producto'].current(idx_prod)
    except ValueError:
        combos['producto'].set(valores[3]) # Fallback a la descripción

    entries['cantidad'].insert(0, valores[4])
    
    # Limpiamos el símbolo $ del precio
    precio_limpio = str(valores[5]).replace('$', '')
    entries['precio'].insert(0, precio_limpio)

    # 4. Bloqueamos ID, Nombre y Producto para que solo editen Cantidad y Precio
    entries['id'].config(state='readonly')
    entries['nombre'].config(state='readonly')
    combos['producto'].config(state='disabled')

def limpiar_formulario_promo(entries, combos):
    """Limpia el formulario y lo deja listo para una nueva alta"""
    entries['id'].config(state='normal')
    entries['nombre'].config(state='normal')
    combos['producto'].config(state='readonly')
    
    for e in entries.values():
        e.delete(0, tk.END)
    combos['producto'].set('')
    
    entries['id'].config(state='readonly')

def guardar_promocion(entries, combos, tree):
    """
    Guarda una promoción nueva o actualiza una existente.
    """
    id_promo = entries['id'].get()
    nombre = entries['nombre'].get()
    cantidad = entries['cantidad'].get()
    precio = entries['precio'].get()

    if not (nombre and cantidad and precio and combos['producto'].get()):
        messagebox.showwarning("Atención", "Por favor complete todos los campos")
        return

    try:
        cantidad = int(cantidad)
        precio = float(precio)
    except ValueError:
        messagebox.showerror("Error", "La cantidad debe ser entera y el precio numérico.")
        return

    # Si hay un ID en el formulario, es una actualización
    if id_promo:
        exito, mensaje = actualizar_promocion(id_promo, cantidad, precio)
    else:
        # Es un alta nueva, buscamos el ID del producto seleccionado
        idx_seleccionado = combos['producto'].current()
        id_producto = combos['prod_ids'][idx_seleccionado]
        exito, mensaje = agregar_promocion(nombre, id_producto, cantidad, precio)

    if exito:
        messagebox.showinfo("Éxito", mensaje)
        limpiar_formulario_promo(entries, combos)
        actualizar_grilla_promociones(tree)
        entries['nombre'].focus()
    else:
        messagebox.showerror("Error", mensaje)

def procesar_cambio_estado(tree, entries, combos):
    """
    Función para alternar entre Alta y Baja lógica
    """
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "Seleccione una promoción de la tabla")
        return

    item = tree.item(seleccion[0])
    valores = item['values']
    
    id_promo = valores[0]
    nombre_promo = valores[1]
    estado_actual = valores[6] # El índice 6 es la nueva columna "Estado"

    # Si está activa la damos de baja (0), si está inactiva la damos de alta (1)
    nuevo_estado = 0 if estado_actual == "Activa" else 1
    palabra_accion = "dar de baja" if nuevo_estado == 0 else "dar de ALTA"

    confirmar = messagebox.askyesno("Confirmar", f"¿Estás seguro de {palabra_accion} la promoción '{nombre_promo}'?")

    if confirmar:
        exito, msj = cambiar_estado_promocion_bd(id_promo, nuevo_estado)
        if exito:
            messagebox.showinfo("Éxito", msj)
            limpiar_formulario_promo(entries, combos)
            actualizar_grilla_promociones(tree)
        else:
            messagebox.showerror("Error", msj)

def mostrar_ventana_promociones(ventana_padre):
    """
    Diseño de ventana de promociones y acciones correspondientes
    """
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Gestión de Promociones (2x1, Combos)")
    ventana.geometry("850x550")
    ventana.resizable(False, False)

    # Formulario de Alta
    frame_form = tk.LabelFrame(ventana, text="Alta / Edición de Promoción", padx=10, pady=10)
    frame_form.pack(fill=tk.X, padx=15, pady=15)

    # Fila 0 (ID Oculto/Solo lectura para control interno)
    tk.Label(frame_form, text="ID Interno:").grid(row=0, column=0, sticky="w")
    entry_id = tk.Entry(frame_form, width=10, state='readonly')
    entry_id.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Fila 1
    tk.Label(frame_form, text="Nombre (Ej: Promo 2x1 Miller):").grid(row=1, column=0, sticky="w")
    entry_nombre = tk.Entry(frame_form, width=30)
    entry_nombre.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
    entry_nombre.focus()

    tk.Label(frame_form, text="Producto:").grid(row=1, column=3, sticky="w")
    combo_producto = ttk.Combobox(frame_form, state="readonly", width=35)
    combo_producto.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

    # Cargar datos en desplegable desde tu lógica de inventario
    productos_activos = listar_producto()
    
    # Armamos la lista para mostrar y la lista oculta con los IDs
    nombres_para_combo = []
    ids_para_combo = []
    
    for p in productos_activos:
        texto_mostrar = f"{p['marca']} {p['capacidad']}L (Cod: {p['id_producto']})"
        nombres_para_combo.append(texto_mostrar)
        ids_para_combo.append(p['id_producto'])

    combo_producto['values'] = nombres_para_combo

    # Fila 2
    tk.Label(frame_form, text="Cantidad Requerida (Ej: 2):").grid(row=2, column=0, sticky="w")
    entry_cantidad = tk.Entry(frame_form, width=15)
    entry_cantidad.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Precio Total Promo ($):").grid(row=2, column=2, sticky="w")
    entry_precio = tk.Entry(frame_form, width=15)
    entry_precio.grid(row=2, column=3, padx=5, pady=5, sticky="w")

    entries = {
        'id': entry_id, 'nombre': entry_nombre, 
        'cantidad': entry_cantidad, 'precio': entry_precio
    }
    combos = {
        'producto': combo_producto,
        'prod_ids': ids_para_combo
    }

    # Botones del formulario
    frame_botones_form = tk.Frame(frame_form)
    frame_botones_form.grid(row=3, column=0, columnspan=6, pady=10)

    boton_guardar = tk.Button(
        frame_botones_form, text="Guardar Promoción", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
        command=lambda: guardar_promocion(entries, combos, tree_promo)
    )
    boton_guardar.pack(side=tk.LEFT, padx=10)

    boton_limpiar = tk.Button(
        frame_botones_form, text="Limpiar Formulario (Nueva Alta)", bg="#2196F3", fg="white", font=("Arial", 9, "bold"),
        command=lambda: limpiar_formulario_promo(entries, combos)
    )
    boton_limpiar.pack(side=tk.LEFT, padx=10)

    # Grilla de Promociones
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    cols = ("ID", "Nombre Promo", "Cod Producto", "Producto", "Lleva", "Precio Total", "Estado")
    tree_promo = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=10)

    # Evento doble clic
    tree_promo.bind("<Double-1>", lambda event: cargar_datos_para_edicion_promo(event, tree_promo, entries, combos))
    
    # Anchos personalizados para que se vea lindo
    anchos = [40, 150, 100, 200, 80, 100, 80]
    for col, ancho in zip(cols, anchos):
        tree_promo.heading(col, text=col)
        tree_promo.column(col, width=ancho, anchor="center")

    tree_promo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree_promo.yview)
    tree_promo.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Botón Baja Lógica
    boton_estado = tk.Button(
        ventana, text="Cambiar Estado Promoción Seleccionada",
        bg="#ff9800", fg="white", font=("Arial", 9, "bold"),
        command=lambda: procesar_cambio_estado(tree_promo, entries, combos)
    )
    boton_estado.pack(fill=tk.X, padx=15, pady=(10, 15))

    # Cargar datos iniciales en la grilla
    actualizar_grilla_promociones(tree_promo)