"""
Modulo de Intefaz grafica
Para ventas al consumidor final
"""

import tkinter as tk
from tkinter import ttk

def crear_vista_ventas(frame_padre):
    """
    Construye la interfaz del modulo de venta y retorna los elementos
    interactivos en un diccionario para su uso en la logica del programa
    """

    # Contenedor principal
    frame_principal = ttk.Frame(frame_padre, padding="10")
    frame_principal.pack(fill=tk.BOTH, expand=True)

    # -- PANEL IZQUIERDO: Carrito y Totales
    panel_izquierdo = ttk.Frame(frame_principal)
    panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    # 1 Tabla del carrito
    columnas = ("codigo", "descripcion", "cantidad", "precio", "subtotal")
    tree_carrito = ttk.Treeview(panel_izquierdo, columns=columnas, show="headings", height=15)

    tree_carrito.heading("codigo", text="Codigo")
    tree_carrito.heading("descripcion", text="Descripcion")
    tree_carrito.heading("cantidad", text="Cant")
    tree_carrito.heading("precio", text="P. Unit")
    tree_carrito.heading("subtotal", text="Subtotal")

    tree_carrito.column("codigo", width=100)
    tree_carrito.column("descripcion", width=250)
    tree_carrito.column("cantidad", width=50, anchor=tk.CENTER)
    tree_carrito.column("precio", width=80, anchor=tk.E)
    tree_carrito.column("subtotal", width=90, anchor=tk.E)

    tree_carrito.pack(fill=tk.BOTH, expand=True)

    # 2 Panel de totales y boton de cobro
    frame_totales = ttk.Frame(panel_izquierdo, padding="10")
    frame_totales.pack(fill=tk.X, pady=(10, 0))

    label_total = ttk.Label(frame_totales, text="TOTAL: $0.00", 
                            font=("Arial", 20, "bold")
    )
    label_total.pack(side=tk.LEFT)

    boton_cobrar = ttk.Button(frame_totales, text="Cobrar (F12)")
    boton_cobrar.pack(side=tk.RIGHT, ipadx=20, ipady=10)

    # -- PANEL DERECHO: Busqueda y Atajos
    panel_derecho = ttk.Frame(frame_principal, width=300)
    panel_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    panel_derecho.pack_propagate(False)

    ttk.Label(panel_derecho, text="Buscar Producto",
              font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

    entry_busqueda = ttk.Entry(panel_derecho, font=("Arial", 14))
    entry_busqueda.pack(fill=tk.X, pady=(0, 5))

    # Lista de Autocompletado (esperando la llamada logica)
    lista_sugerencias = tk.Listbox(panel_derecho, font=("Arial", 11), height=5)

    frame_acciones = ttk.Frame(panel_derecho)
    frame_acciones.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 20))

    ttk.Separator(frame_acciones, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

    ttk.Label(frame_acciones, text="Acciones", 
              font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))

    boton_ajuste = ttk.Button(frame_acciones, text="Ajuste / Descuento (F5)")
    boton_ajuste.pack(fill=tk.X, pady=5, ipady=5)

    boton_eliminar_item = ttk.Button(frame_acciones, text="Quitar Item (Supr)")
    boton_eliminar_item.pack(fill=tk.X, pady=5, ipady=5)

    boton_cancelar = ttk.Button(frame_acciones, text="Cancelar Venta (Esc)")
    boton_cancelar.pack(fill=tk.X, padx=5, ipady=5)

    # Retornamos los widgets esenciales para que el controlador pueda asignarles eventos
    return {
        "frame_principal": frame_principal,
        "tree_carrito": tree_carrito,
        "label_total": label_total,
        "boton_cobrar": boton_cobrar,
        "entry_busqueda": entry_busqueda,
        "lista_sugerencias": lista_sugerencias,
        "boton_ajuste": boton_ajuste,
        "boton_eliminar": boton_eliminar_item,
        "boton_cancelar": boton_cancelar
    }

def abrir_modulo_ventas(ventana_padre):
    """
    Punto de entaada al modulo de ventas
    """

    # 1 Creamos la ventana secundaria
    ventana_ventas = tk.Toplevel(ventana_padre)
    ventana_ventas.title("Negocio Fresa - Punto de Venta")
    ventana_ventas.geometry("1024x768")

    # 2 Instanciamos la interfaz dentro de la nueva ventana
    widgets_ventas = crear_vista_ventas(ventana_ventas)

    # 3 Importamos el controlador y conectamos lo eventos
    from logica.controlador_ventas import configurar_eventos_ventas
    configurar_eventos_ventas(widgets_ventas)
