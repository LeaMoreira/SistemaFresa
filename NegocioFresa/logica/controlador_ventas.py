"""
Modulo para el carro de compras y el control de productos
para la venta en el negocio
"""

import tkinter as tk
from tkinter import messagebox
from base_datos.conexion import obtener_conexion

# Variable global a nivel de módulo para mantener el estado del carrito activo
carrito_actual = []

def configurar_eventos_ventas(widgets):
    """
    Controlador que vincula la lógica del negocio con la interfaz de Tkinter
    Recibe el diccionario 'widgets' generado por 'crear_vista_ventas'
    """
    entry_busqueda = widgets["entry_busqueda"]
    lista_sugerencias = widgets["lista_sugerencias"]
    tree_carrito = widgets["tree_carrito"]
    label_total = widgets["label_total"]

    # Acciones de Botones
    boton_eliminar = widgets["boton_eliminar"]
    boton_cancelar = widgets["boton_cancelar"]

    def agregar_al_carrito(id_prod, descripcion, precio_unitario):
        """
        Verifica si el producto ya esta en el carrito
        Si esta, suma en 1 a la cantidad y recalcula el subtotal
        Si no, lo agrega a un nuevo renglon
        """

        precio_unitario = float(precio_unitario)

        # 1 Buscamos si el producto ya existe en nuestra logica
        for item in carrito_actual:
            if item['id_producto'] == id_prod:
                # Actualizamos la suma
                item['cantidad'] += 1
                item['subtotal_linea'] = item['cantidad'] * item['precio_unitario']

                # Buscamos el renglon exacto en la tabla para actualizar
                for child in tree_carrito.get_children():
                    valores_fila = tree_carrito.item(child, "values")
                    if str(valores_fila[0]) == str(id_prod):
                        # Actualizamos la fila mostrando Precio y Subtotal correctamente
                        tree_carrito.item(child, values=(
                            id_prod,
                            descripcion,
                            item['cantidad'],
                            f"${precio_unitario:.2f}",
                            f"${item['subtotal_linea']:.2f}"
                        ))
                        break

                actualizar_total_visual()
                return # Aca se corta la funcion si ya se sumo

        # 2 Si el bucle termino y no encontro le producto, lo creamos de cero
        nuevo_item = {
            'id_producto': id_prod,
            'descripcion': descripcion,
            'cantidad': 1,
            'precio_unitario': precio_unitario,
            'subtotal_linea': precio_unitario,
            'tipo_linea': 'PRODUCTO'
        }
        carrito_actual.append(nuevo_item)

        # Insertamos el renglon nuevo Precio y Subtotal arrancan iguales
        tree_carrito.insert("", tk.END, values=(
            id_prod,
            descripcion,
            1,
            f"${precio_unitario:.2f}",
            f"${precio_unitario:.2f}"
        ))
        actualizar_total_visual()

    def actualizar_total_visual():
        """
        Recalcula y actualiza la etiqueta del TOTAL en pantalla
        """
        total = sum(item['subtotal_linea'] for item in carrito_actual)
        label_total.config(text=f"TOTAL: ${total:.2f}")

    def cancelar_venta(event=None):
        """
        Limpiamos todo el carrito y reiniciamos la pantalla de ventas
        """

        if not carrito_actual:
            return

        respuesta = messagebox.askyesno("Confirmar", "Estas seguro de cancelar la venta?")
        if respuesta:
            carrito_actual.clear()
            for fila in tree_carrito.get_children():
                tree_carrito.delete(fila)

            entry_busqueda.delete(0, tk.END)
            actualizar_total_visual()

    def eliminar_item(event=None):
        """
        Eliminamos el producto seleccionado actualmente en el treeview
        """

        seleccionado = tree_carrito.selection()
        if not seleccionado:
            messagebox.showinfo("AVISO", "Primero debes seleccionar el producto de la lista")
            return

        item_id = seleccionado[0]
        valores_fila = tree_carrito.item(item_id, "values")
        id_prod = valores_fila[0]

        # 1 Quitamos la estructura logica
        for i, item in enumerate(carrito_actual):
            if str(item['id_producto']) == str(id_prod):
                del carrito_actual[i]
                break

        # 2 Lo quietamos de la vista del treeview
        tree_carrito.delete(item_id)

        # 3 Recalculamos el total
        actualizar_total_visual()

    def al_teclear_busqueda(event):
        """
        Evento que se dispara cada vez que se suelta una tecla en el buscador
        """
        # Ignorando teclas de navegacion para evitar bugs visuales
        if event.keysym in ['Up', 'Down', 'Return', 'Escape']:
            return

        texto = entry_busqueda.get().strip()

        # Si el usuario escribio 2 o mas letras, buscamos
        if len(texto) >= 2:
            try:
                conexion = obtener_conexion()
                cursor = conexion.cursor()

                # Buscamos coincidencias en el ID de codigo de barra o el nombre
                query = '''
                        SELECT p.id_producto,
                            m.nombre || ' ' || c.litros || ' L' AS descripcion,
                            p.precio_venta
                        FROM productos p
                        JOIN marcas m ON p.id_marca = m.id
                        JOIN capacidades c ON p.id_capacidad = c.id
                        WHERE (p.id_producto LIKE ? OR m.nombre LIKE ?) AND p.estado = 1
                        LIMIT 10
                '''
                parametro_busqueda = f"%{texto}%"
                cursor.execute(query, (parametro_busqueda, parametro_busqueda))
                resultado_db = cursor.fetchall()

                # CORRECCIÓN 1: 'delete' en lugar de 'detele'
                lista_sugerencias.delete(0, tk.END)

                if resultado_db:
                    for fila in resultado_db:
                        # fila [0] = id, fila[1] = nombre, fila[2] = precio
                        lista_sugerencias.insert(tk.END, f"{fila[0]} | {fila[1]} | ${fila[2]}")

                    x = entry_busqueda.winfo_x()
                    y = entry_busqueda.winfo_y() + entry_busqueda.winfo_height()
                    lista_sugerencias.place(x=x, y=y, width=entry_busqueda.winfo_width())
                else:
                    lista_sugerencias.place_forget()

            except Exception as e:
                print(f"ERROR al buscar en DB: {e}")

            finally:
                conexion.close()
        else:
            lista_sugerencias.place_forget()

    # ¡ATENCIÓN! ESTA FUNCIÓN AHORA ESTÁ AL MISMO NIVEL QUE al_teclear_busqueda
    def procesar_codigo_barras(event):
        """
        Captura el 'ENTER' automático del lector o del usuario al buscar manualmente.
        """
        # ✨ MEJORA DE UX: Si la lista flotante está visible y apretás Enter, 
        # asume que querés el primer elemento de esa lista.
        if lista_sugerencias.winfo_ismapped() and lista_sugerencias.size() > 0:
            lista_sugerencias.selection_set(0) # Selecciona el índice 0 (el primero)
            seleccionar_producto(None) # Ejecuta la función de agregar al carrito
            return # Corta la ejecución acá para no hacer la búsqueda de código de barras

        codigo = entry_busqueda.get().strip()
        if not codigo:
            return

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Buscamos coincidencias EXACTAS con el ID del producto que lee
            query = '''
                    SELECT p.id_producto, 
                           m.nombre || ' ' || c.litros || ' L' AS descripcion, 
                           p.precio_venta
                    FROM productos p
                    JOIN marcas m ON p.id_marca = m.id
                    JOIN capacidades c ON p.id_capacidad = c.id
                    WHERE p.id_producto = ? AND p.estado = 1
            '''
            cursor.execute(query, (codigo,)) 
            producto_db = cursor.fetchone()

            if producto_db:
                # Si existe, lo metemos directo al carrito
                id_prod, descripcion, precio_unitario = producto_db

                # Usamos la funcion centralizada
                agregar_al_carrito(id_prod, descripcion, precio_unitario)

                # Limpiamos todos los datos para escanear nuevo producto
                entry_busqueda.delete(0, tk.END)
                lista_sugerencias.place_forget()

            else:
                # Si escaneo y el producto no esta cargado, se da señal
                messagebox.showwarning("Atención", "El código escaneado no corresponde a un producto registrado")
                entry_busqueda.delete(0, tk.END)
                lista_sugerencias.place_forget()

        except Exception as e:
            print(f"Error al procesar el código de barra: {e}")
        finally:
            conexion.close()

    # AL MISMO NIVEL DE INDENTACIÓN
    def seleccionar_producto(event):
        """
        Pasa el producto seleccionado de la lista flotante al carrito
        """
        # CORRECCIÓN 2: 'curselection' en lugar de 'curseleccion'
        seleccion = lista_sugerencias.curselection()
        if not seleccion:
            return

        texto_item = lista_sugerencias.get(seleccion[0])
        # Separamos el texto por la barra "|" para sacar los datos
        partes = texto_item.split(" | ")
        id_prod = partes[0]
        descripcion = partes[1]
        precio_unitario = float(partes[2].replace("$", ""))

        # Usamos la nueva funcion centralizada
        agregar_al_carrito(id_prod, descripcion, precio_unitario)

        # 3 Limpiamos todo para la proxima busqueda
        entry_busqueda.delete(0, tk.END)
        lista_sugerencias.place_forget()

        # Devolvemos el foco al buscador para que la cajera siga escaneando sin usar el mouse
        entry_busqueda.focus_set()

    def mover_foco_a_lista(event):
        """Maneja las flechas de teclado para bajar del entry a la lista"""
        if lista_sugerencias.winfo_ismapped():
            lista_sugerencias.focus_set()
            lista_sugerencias.selection_set(0)

    # -- ASIGNACION DE EVENTOS BIND (Ahora sí están al nivel correcto para ejecutarse al abrir la ventana) --
    entry_busqueda.bind("<KeyRelease>", al_teclear_busqueda)
    
    # Permitir seleccionar con doble clic o con la tecla enter en la lista
    lista_sugerencias.bind("<Double-Button-1>", seleccionar_producto)
    lista_sugerencias.bind("<Return>", seleccionar_producto)

    # Teclas especiales en el Entry
    entry_busqueda.bind("<Escape>", cancelar_venta)
    entry_busqueda.bind("<Delete>", eliminar_item)
    entry_busqueda.bind("<Down>", mover_foco_a_lista)
    entry_busqueda.bind("<Return>", procesar_codigo_barras)

    # Tecla especiales de Treeview
    tree_carrito.bind("<Escape>", cancelar_venta)
    tree_carrito.bind("<Delete>", eliminar_item)

    # Asignacion de Command (clics en los botones)
    boton_cancelar.config(command=cancelar_venta)
    boton_eliminar.config(command=eliminar_item)