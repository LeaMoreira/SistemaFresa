"""
Ventana de inventario por tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from logica.inventario import registrar_marca, registrar_capacidad, listar_marcas, listar_capacidades

def actualizar_grillas(tree_marcas, tree_capacidades):
    """
    Limpia las tablas y vuelve a cargar los datos desde la base de datos
    Es una adaptación del patron observer: actualiza la vista tras un cambio
    """

    # 1 Limpia datos viejos
    for item in tree_marcas.get_children():
        tree_marcas.delete(item)
    for item in tree_capacidades.get_children():
        tree_capacidades.delete(item)

    # 2 Cargar Marcas
    for marca in listar_marcas():
        tree_marcas.insert("", tk.END, values=(marca['id'], marca['nombre']))

    # 3 Cargar Capacidades
    for cap in listar_capacidades():
        tree_capacidades.insert("", tk.END, values=(cap['id'], f"{cap['litros']} L"))

def procesar_nueva_marca(entry, tree_marcas, tree_capacidades):
    """
    Procesa el ingreso de una nueva marca desde la ventana de inventario
    """

    nombre = entry.get()
    if not nombre:
        messagebox.showwarning("Atencion", "El nombre de la marca no puede estar vacio")
        return

    if registrar_marca(nombre):
        messagebox.showinfo("Exito", f"Marca '{nombre}' registrada correctamente")
        entry.delete(0, tk.END)
        actualizar_grillas(tree_marcas, tree_capacidades)
    else:
        messagebox.showerror("Error", f"La marca '{nombre}' ya existe o hubo un error al registrarla")

def procesar_nueva_capacidad(entry, tree_marcas, tree_capacidades):
    """
    Procesa el ingreso de una nueva capacidad desde la ventana de inventario
    """

    litros = entry.get()
    if not litros:
        messagebox.showwarning("Atencion", "Ingrese la capacidad en litros")
        return

    if registrar_capacidad(litros):
        messagebox.showinfo("Exito", "Capacidad registrada correctamente")
        entry.delete(0, tk.END)
        actualizar_grillas(tree_marcas, tree_capacidades)
    else:
        messagebox.showerror("Error", f"La capacidad '{litros}' ya existe o hubo un error al registrarla")

def mostrar_ventana_parametros(ventana_padre):
    """
    Dibuja la ventana para gestionar el D2 Archivo Parametro (Marcas y Capacidades)
    """

    # Usamos Toplevel para que sea una vientana hija
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Gestion de Parametros - Marcas y Capacidades")
    ventana.geometry("700x450")
    ventana.resizable(False, False )

    # Izquierda - Marcas
    frame_marcas = tk.LabelFrame(ventana, text="Gestion Marcas", padx=10, pady=10)
    frame_marcas.place(x=20, y=20, width=320, height=400)

    tk.Label(frame_marcas, text="Nombre de Marca:").pack(anchor="w")
    entry_marca = tk.Entry(frame_marcas, width=30)
    entry_marca.pack(anchor="w", pady=5)

    # Grilla (Treeview) para Marcas
    columnas_marcas = ("ID", "Nombre")
    tree_marcas = ttk.Treeview(frame_marcas, columns=columnas_marcas,
                                show="headings", height=10)
    tree_marcas.heading("ID", text='ID')
    tree_marcas.heading("Nombre", text="Nombre")
    tree_marcas.column("ID", width=50)
    tree_marcas.column("Nombre", width=200)
    tree_marcas.pack(pady=10)

    boton_marca = tk.Button(frame_marcas, text="Guardar Marca", bg="#4CAF50", fg="white",
                            command=lambda: procesar_nueva_marca(entry_marca, tree_marcas, tree_capacidades)
    )
    boton_marca.pack(fill=tk.X )

    # Derecha - Capacidades
    frame_cap = tk.LabelFrame(ventana, text="Gestion de Capacidades", padx=10, pady=10)
    frame_cap.place(x=360, y=20, width=320, height=400)

    tk.Label(frame_cap, text="Litros (ejemplo: 1.5, 2.25):").pack(anchor="w")
    entry_capacidad = tk.Entry(frame_cap, width=30)
    entry_capacidad.pack(pady=5, anchor="w")

    # Grilla (Treeview) para Capacidades
    columnas_cap = ("ID", "Litros")
    tree_capacidades = ttk.Treeview(frame_cap, columns=columnas_cap, show="headings", height=10)
    tree_capacidades.heading("ID", text="ID")
    tree_capacidades.heading("Litros", text="Capacidad")
    tree_capacidades.column("ID", width=50)
    tree_capacidades.column("Litros", width=200)
    tree_capacidades.pack(pady=10)

    boton_cap = tk.Button(frame_cap, text="Guardar Capacidad", bg="#2196F3", fg="white",
                          command=lambda: procesar_nueva_capacidad(entry_capacidad, tree_marcas, tree_capacidades)
    )
    boton_cap.pack(fill=tk.X)

    # Cargar los datos iniciales al abrir la ventana
    actualizar_grillas(tree_marcas, tree_capacidades)
