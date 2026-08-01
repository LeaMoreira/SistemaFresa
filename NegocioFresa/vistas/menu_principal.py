"""
Tablero principal de la aplicacion
tiene botones aun inactivos
"""

import tkinter as tk
from vistas.ventana_inventario import mostrar_ventana_parametros
from vistas.ventana_producto import mostrar_ventana_productos
from vistas.ventana_ventas import abrir_modulo_ventas
from vistas.ventana_promociones import mostrar_ventana_promociones

def mostrar_menu_principal(usuario_actual):
    """
    Renderizamos la ventana del menu principal
    luego del login correcto
    """

    ventana = tk.Tk()
    ventana.title(f"Negocio Fresa - Panel de Control (Usuario: {usuario_actual['usuario']})")
    ventana.geometry("600x400")
    ventana.resizable(False, False)

    # Titulo
    tk.Label(ventana, text="Menu Principal",
             font=("Arial", 16, "bold")).pack(pady=(20))
    
    # Un marco para agrupar los botones de ordenes
    marco_botones = tk.Frame(ventana)
    marco_botones.pack(expand=True)

    # Botones de los procesos del DFD (inactivos por ahora)
    tk.Button(marco_botones, text="1. Gestión de Parámetros",
                width=25, height=2,
                command=lambda: mostrar_ventana_parametros(ventana)).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(marco_botones, text="2. Gestión de Productos", 
                width=25, height=2,
                command=lambda: mostrar_ventana_productos(ventana)).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(marco_botones, text="3. Promociones",
            width=25, height=2,
            command=lambda: mostrar_ventana_promociones(ventana)).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(marco_botones, text="4. Ventas",
            width=25, height=2,
            command=lambda: abrir_modulo_ventas(ventana)).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(marco_botones, text="5. Reportes",
            width=25, height=2).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    ventana.mainloop()
