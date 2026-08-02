"""
Modulo interfaz grafica para reportes
utiliza pestañas tipo notebook para separar balances, rotacion y alerta de stock
"""

import tkinter as tk
from tkinter import ttk
from logica.reportes import(
    obtener_balance_ventas,
    obtener_productos_mas_vendidos,
    obtener_estado_inventario
)

def crear_ventana_reportes(ventana_padre):
    """
    Construye la ventana principal de reportes y sus 3 pestañas
    """

    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Reportes y Estadisticas de Ventas")
    ventana.geometry("900x600")

    # Contenedor principal de pestañas
    notebook = ttk.Notebook(ventana)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # -- Pestaña de Balance Financiero
    tab_balance = ttk.Frame(notebook)
    notebook.add(tab_balance, text="Balance Financiero")

    # Controles superiores
    frame_filtros_1 = tk.Frame(tab_balance)
    frame_filtros_1.pack(fill=tk.X, padx=20, pady=15)

    tk.Label(frame_filtros_1, text="Filtrar por:",
            font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))

    combo_filtro_balance = ttk.Combobox(frame_filtros_1,
                                        values=["Hoy", "Este Mes", "Historico"],
                                        state="readonly", width=15)
    combo_filtro_balance.set("Hoy")
    combo_filtro_balance.pack(side=tk.LEFT)
    combo_filtro_balance.pack(side=tk.LEFT)

    # Etiqueta de Gran Total
    label_gran_total = tk.Label(tab_balance, text="RECAUDACION TOTAL: $0.00",
                                font=("Arial", 16, "bold"), fg="#2E7D32")
    label_gran_total.pack(pady=(0, 15))

    # Grilla de desglose
    cols_balance = ("Metodo de Pago", "Cant. Operaciones", "Total Recaudado")
    tree_balance = ttk.Treeview(tab_balance, columns=cols_balance, show="headings", height=10)
    for col in cols_balance:
        tree_balance.heading(col, text=col)
        tree_balance.column(col, anchor="center")
    tree_balance.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def actualizar_tab_balance(event=None):
        # Mapea la seleccion visual de parametro
        mapeo = {"Hoy": "hoy", "Este Mes": "mes", "Historico": "historico"}
        filtro_backend = mapeo.get(combo_filtro_balance.get(), "hoy")

        datos = obtener_balance_ventas(filtro_backend)

        # Actualiza etiqueta de total
        label_gran_total.config(text=f"RECAUDACION TOTAL: ${datos['gran_total']:.2f}")

        # Actualiza Grilla
        for item in tree_balance.get_children():
            tree_balance.delete(item)

        for fila in datos['desglose']:
            tree_balance.insert("", tk.END, values=(
                fila['metodo_pago'],
                fila['cantidad_operaciones'],
                f"${fila['total_recaudado']:.2f}"
            ))

    combo_filtro_balance.bind("<<ComboboxSelected>>", actualizar_tab_balance)

    # -- Pestaña Rotacion Productos Mas Vendidos
    tab_rotacion = ttk.Frame(notebook)
    notebook.add(tab_rotacion, text="Productos Mas Vendidos")

    frame_filtros_2 = tk.Frame(tab_rotacion)
    frame_filtros_2.pack(fill=tk.X, padx=20, pady=15)

    tk.Label(frame_filtros_2, text="Filtrar por:",
             font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
    combo_filtro_rotacion = ttk.Combobox(frame_filtros_2, values=["Hoy", "Este Mes", "Histórico"], state="readonly", width=15)
    combo_filtro_rotacion.set("Este Mes") # Por defecto, ver el mes suele ser más útil para stock
    combo_filtro_rotacion.pack(side=tk.LEFT)

    cols_rotacion = ("Cod. Producto", "Descripción", "Unidades Vendidas", "Ingreso Generado")
    tree_rotacion = ttk.Treeview(tab_rotacion, columns=cols_rotacion, show="headings", height=15)
    
    anchos_rotacion = [100, 300, 120, 150]
    for col, ancho in zip(cols_rotacion, anchos_rotacion):
        tree_rotacion.heading(col, text=col)
        tree_rotacion.column(col, width=ancho, anchor="center")
    
    tree_rotacion.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def actualizar_tab_rotacion(event=None):
        mapeo = {"Hoy": "hoy", "Este Mes": "mes", "Histórico": "historico"}
        filtro_backend = mapeo.get(combo_filtro_rotacion.get(), "mes")
        
        for item in tree_rotacion.get_children():
            tree_rotacion.delete(item)
            
        for fila in obtener_productos_mas_vendidos(filtro_backend):
            tree_rotacion.insert("", tk.END, values=(
                fila['id_producto'],
                fila['descripcion_producto'],
                fila['total_unidades_vendidas'],
                f"${fila['recaudacion_total']:.2f}"
            ))

    combo_filtro_rotacion.bind("<<ComboboxSelected>>", actualizar_tab_rotacion)

    # =========================================================================
    # PESTAÑA 3: ALERTAS DE STOCK (SEMÁFORO)
    # =========================================================================
    tab_alertas = ttk.Frame(notebook)
    notebook.add(tab_alertas, text="Alertas de Stock (Compras)")

    tk.Label(tab_alertas, text="Control visual de inventario para reposición", font=("Arial", 12, "bold")).pack(pady=10)

    cols_stock = ("Cod", "Producto", "Stock Actual", "Stock Mínimo")
    tree_stock = ttk.Treeview(tab_alertas, columns=cols_stock, show="headings", height=20)
    
    anchos_stock = [80, 400, 100, 100]
    for col, ancho in zip(cols_stock, anchos_stock):
        tree_stock.heading(col, text=col)
        tree_stock.column(col, width=ancho, anchor="center")
    
    # Configuración de los colores (Tags) del semáforo
    tree_stock.tag_configure("rojo", background="#ffcccc", foreground="black")      # Faltante total
    tree_stock.tag_configure("amarillo", background="#fff3cd", foreground="black")  # En alerta (por debajo del mínimo)
    tree_stock.tag_configure("verde", background="#d4edda", foreground="black")     # Stock sano

    tree_stock.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def actualizar_tab_alertas():
        for item in tree_stock.get_children():
            tree_stock.delete(item)
            
        for fila in obtener_estado_inventario():
            stock_actual = fila['stock_actual']
            stock_minimo = fila['stock_minimo']
            
            # Lógica del semáforo
            if stock_actual <= 0:
                tag = "rojo"
            elif stock_actual <= stock_minimo:
                tag = "amarillo"
            else:
                tag = "verde"
                
            tree_stock.insert("", tk.END, values=(
                fila['id_producto'],
                fila['descripcion'],
                stock_actual,
                stock_minimo
            ), tags=(tag,))

    # =========================================================================
    # CARGA INICIAL DE DATOS
    # =========================================================================
    actualizar_tab_balance()
    actualizar_tab_rotacion()
    actualizar_tab_alertas()