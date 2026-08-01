"""
Modulo de Intefaz grafica
Para ventas al consumidor final
"""

import tkinter as tk
from tkinter import ttk, messagebox

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

def crear_modal_cobro(parent, subtotal_compra, callback_confirmar):
    """
    Crea la interfaz visual del modal de cobro (Vista pura).
    """
    modal = tk.Toplevel(parent)
    modal.title("Procesar Pago")
    modal.geometry("350x450")
    modal.resizable(False, False)
    modal.grab_set()

    # Diccionario temporal (Simula la futura tabla para RF 9.3)
    recargos_pago = {
        "Efectivo": 0.0,
        "Mercado Pago": 0.0,
        "Tarjeta": 10.0
    }

    # 1. Declaración de variables de control
    var_metodo = tk.StringVar(value="Efectivo")
    var_paga_con = tk.StringVar(value="")
    var_recargo = tk.DoubleVar(value=0.0)
    var_total_final = tk.DoubleVar(value=subtotal_compra)
    var_vuelto = tk.StringVar(value="0.00")

    # 2. Función interna de recálculo (debe estar BIEN INDENTADA aquí adentro)
    def recalcular(*args):
        metodo = var_metodo.get()
        porcentaje = recargos_pago.get(metodo, 0.0)
        monto_recargo = subtotal_compra * (porcentaje / 100.0)
        var_recargo.set(monto_recargo)
        
        total_actualizado = subtotal_compra + monto_recargo
        var_total_final.set(total_actualizado)
        
        try:
            paga = float(var_paga_con.get().replace('$', '').strip())
            if paga >= total_actualizado:
                var_vuelto.set(f"{paga - total_actualizado:.2f}")
            else:
                var_vuelto.set("0.00")
        except ValueError:
            var_vuelto.set("0.00")

    var_metodo.trace_add("write", recalcular)
    var_paga_con.trace_add("write", recalcular)

    # 3. Diseño de la interfaz visual
    marco = tk.LabelFrame(modal, text="Detalles del Cobro", padx=15, pady=15)
    marco.pack(padx=20, pady=20, fill="both", expand=True)

    tk.Label(marco, text="Subtotal:").grid(row=0, column=0, sticky="w", pady=5)
    tk.Label(marco, text=f"${subtotal_compra:.2f}", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="e")

    tk.Label(marco, text="Método de Pago:").grid(row=1, column=0, sticky="w", pady=5)
    combo_metodo = ttk.Combobox(marco, textvariable=var_metodo, values=list(recargos_pago.keys()), state="readonly")
    combo_metodo.grid(row=1, column=1, pady=5)

    tk.Label(marco, text="Recargos/Imp.:").grid(row=2, column=0, sticky="w", pady=5)
    tk.Label(marco, textvariable=var_recargo).grid(row=2, column=1, sticky="e")

    tk.Label(marco, text="TOTAL A PAGAR:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", pady=15)
    tk.Label(marco, textvariable=var_total_final, font=("Arial", 12, "bold"), fg="red").grid(row=3, column=1, sticky="e")

    tk.Label(marco, text="Paga con $:").grid(row=4, column=0, sticky="w", pady=5)
    entry_paga = tk.Entry(marco, textvariable=var_paga_con, justify="right")
    entry_paga.grid(row=4, column=1, pady=5)
    entry_paga.focus()

    tk.Label(marco, text="Vuelto:").grid(row=5, column=0, sticky="w", pady=5)
    tk.Label(marco, textvariable=var_vuelto, font=("Arial", 11, "bold"), fg="green").grid(row=5, column=1, sticky="e")

    # 4. Función de confirmación
    def al_confirmar():
        try:
            paga = float(var_paga_con.get().replace('$', '').strip())
        except ValueError:
            paga = 0.0

        if paga < var_total_final.get() and var_metodo.get() == "Efectivo":
            messagebox.showwarning("Atención", "El monto ingresado es menor al total a pagar.")
            return

        exito = callback_confirmar(var_metodo.get(), var_recargo.get(), var_total_final.get())
        
        if exito:
            modal.destroy()

    boton_confirmar = tk.Button(modal, text="Confirmar Venta", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=al_confirmar)
    boton_confirmar.pack(pady=10, fill="x", padx=20)

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
