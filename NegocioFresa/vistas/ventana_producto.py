"""
Ventana que permite:
    Escanear/ingresar ID producto
    Seleccionar la Marca y Capacidad desde menu desplegables llenados dinamicamente
        con las marcas que cargaron antes
    Cargar precios independientes de comrpa/venta y stock inicial
    Dar baja logica o actualizar stock en (RF5, RF6, RF7)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from logica.inventario import (
    registrar_producto, listar_producto,
    listar_marcas, listar_capacidades,
    dar_baja_logica_producto
)

def actualizar_grilla_productos(tree):
    """
    Limpia y recarga la lista de productos en el Treeview
    """

    for item in tree.get_children():
        tree.delete(item)

    for p in listar_producto():
        tree.insert("", tk.END, values=(
            p['id_producto'],
            p['marca'],
            f"{p['capacidad']} L",
            f"${p['precio_compra']:.2f}",
            f"${p['precio_venta']:.2f}",
            p['stock_actual'],
            p['stock_minimo']
            )
        )

def guardar_producto(entries, combos, tree):
    """
    Guardamos los productos cargados o escaneados
    """

    id_p = entries['id'].get()
    p_compra = entries['p_compra'].get()
    p_venta = entries['p_venta'].get()
    stock = entries['stock'].get()
    s_min = entries['stock_min'].get()

    # Recuperamos el ID seleccionado en las listas desplegables
    marca_sel = combos['marca'].get()
    cap_sel = combos['capacidad'].get()

    if not (id_p and p_compra and p_venta and stock and s_min and marca_sel and cap_sel):
        messagebox.showwarning("Atencion", "Por favor complete todos los campos")
        return

    # Extraemos los IDs que guardamos de fondo en las opciones del Combobox
    id_marca = combos['marca_ids'][combos['marca'].current()]
    id_capacidad = combos['cap_ids'][combos['capacidad'].current()]

    exito, mensaje = registrar_producto(
        id_p, id_marca, id_capacidad, p_compra, p_venta, stock, s_min
    )

    if exito:
        messagebox.showinfo("Exito", mensaje)
        # Limpiar formulario
        for e in entries.values():
            e.delete(0, tk.END)
        actualizar_grilla_productos(tree)
        # Enfocar de nuevo el campo ID para recibir el proximo escaneado
        entries['id'].focus()
    else:
        messagebox.showerror("Error", mensaje)

def procesar_baja(tree):
    """
    Funcion para baja por seleccion de tabla treeview
    """

    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Atencion", "Seleccione un producto de la tabla para dar de baja")
        return

    item = tree.item(seleccion[0])
    id_producto = item['values'][0]

    confirmar = messagebox.askyesno("Confirmar Baja", f"Estas seguro en dar de baja el producto ID: {id_producto}")
    if confirmar:
        exito, msj = dar_baja_logica_producto(id_producto)
        if exito:
            messagebox.showinfo("Exito", msj)
            actualizar_grilla_productos(tree)
        else:
            messagebox.showerror("Error", msj)

def mostrar_ventana_productos(ventana_padre):
    """
    Diseño de ventana de productos y acciones correspondientes
    """

    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Gestion de Productos e Inventario")
    ventana.geometry("850x550")
    ventana.resizable(False, False)

    # Formulario de Alta
    frame_form = tk.LabelFrame(ventana, text="Alta/Registro de Producto", padx=10, pady=10)
    frame_form.pack(fill=tk.X, padx=15, pady=15)

    # Fila 1
    tk.Label(frame_form, text="Codigo/ID Barcode:").grid(row=0, column=0, sticky="w")
    entry_id = tk.Entry(frame_form, width=20)
    entry_id.grid(row=0, column=1, padx=5, pady=5)
    entry_id.focus() # Foco preparado para la lectora de codigo

    tk.Label(frame_form, text="Marca").grid(row=0, column=2, sticky="w")
    combo_marca = ttk.Combobox(frame_form, state="readonly", width=18)
    combo_marca.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_form, text="Capacidad:").grid(row=0, column=4, sticky="w")
    combo_capacidad = ttk.Combobox(frame_form, state="readonly", width=15)
    combo_capacidad.grid(row=0, column=5, padx=5, pady=5)

    # Cargar datos en desplegables
    marcas = listar_marcas()
    capacidades = listar_capacidades()

    combo_marca['values'] = [m['nombre'] for m in marcas]
    combo_capacidad['values'] = [f"{c['litros']} L" for c in capacidades]

    # Fila 2
    tk.Label(frame_form, text="Precio Compra ($):").grid(row=1, column=0, sticky="w")
    entry_p_compra = tk.Entry(frame_form, width=20)
    entry_p_compra.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Precio Venta ($):").grid(row=1, column=2, sticky="w")
    entry_p_venta = tk.Entry(frame_form, width=20)
    entry_p_venta.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(frame_form, text="Stock Inicial:").grid(row=1, column=4, sticky="w")
    entry_stock = tk.Entry(frame_form, width=15)
    entry_stock.grid(row=1, column=5, padx=5, pady=5)

    # Fila 3
    tk.Label(frame_form, text="Stock Minimo:").grid(row=2, column=0, sticky="w")
    entry_stock_min = tk.Entry(frame_form, width=20)
    entry_stock_min.grid(row=2, column=1, padx=5, pady=5)

    entries = {
        'id': entry_id, 'p_compra': entry_p_compra, 'p_venta': entry_p_venta,
        'stock': entry_stock, 'stock_min': entry_stock_min
    }
    combos = {
        'marca': combo_marca, 'capacidad': combo_capacidad,
        'marca_ids': [m['id'] for m in marcas],
        'cap_ids': [c['id'] for c in capacidades]
    }

    boton_guardar = tk.Button(
        frame_form, text="Guardar Producto", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
        command=lambda: guardar_producto(entries, combos, tree_prod)
    )
    boton_guardar.grid(row=2, column=3, columnspan=3, sticky="ew", padx=5, pady=5)

    # Grilla de Productos
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    cols = ("ID", "Marca", "Capacidad", "P. Compra", "P. Venta", "Stock", "Stock Min")
    tree_prod = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=10)

    for col in cols:
        tree_prod.heading(col, text=col)
        tree_prod.column(col, width=100, anchor="center")

    tree_prod.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree_prod.yview)
    tree_prod.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Boton Baja Logica
    boton_baja = tk.Button(
        ventana, text="Dar Baja Producto Seleccionado RF5",
        bg="#f44336", fg="white",
        command=lambda: procesar_baja(tree_prod)
    )
    boton_baja.pack(fill=tk.X, padx=15, pady=10)

    # Cargar datos en la grilla
    actualizar_grilla_productos(tree_prod)
