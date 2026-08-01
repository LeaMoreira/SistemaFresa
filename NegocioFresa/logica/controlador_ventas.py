"""
Modulo para el carro de compras y el control de productos
para la venta en el negocio
"""

import tkinter as tk
from tkinter import ttk, messagebox
from base_datos.conexion import obtener_conexion
from logica.ventas import registrar_venta_transaccion
from vistas.ventana_ventas import crear_modal_cobro
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
    boton_cobrar = widgets["boton_cobrar"]

    def agregar_al_carrito(id_prod, descripcion, precio_unitario):
        """
        Verifica si el producto ya esta en el carrito
        si esta, suma en 1 la cantidad y recalcula el subtotal (aplica promos si es necesario)
        Si no lo agrega en un nuevo renglon
        """

        precio_unitario = float(precio_unitario)  # Aseguramos que sea float

        # Funcion para calcular promociones
        def calcular_subtotal(cantidad_actual):
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            try:
                # Buscamos si este producto tiene promocion activa
                cursor.execute('''
                    SELECT cantidad_requerida, precio_promo
                    FROM promociones
                    WHERE id_producto = ? AND estado = 1
                ''', (id_prod,))
                promo = cursor.fetchone()

                if promo:
                    cant_req = promo['cantidad_requerida']
                    precio_promo = promo['precio_promo']

                    # calculamos las ofertas
                    paquetes_prmo = cantidad_actual // cant_req
                    unidades_sueltas = cantidad_actual % cant_req

                    return (paquetes_prmo * precio_promo) + (unidades_sueltas * precio_unitario)
                else:
                    return cantidad_actual * precio_unitario
            except Exception as e:
                print(f"Error al calcular promociones: {e}")
                return cantidad_actual * precio_unitario
            finally:
                conexion.close()

        # 1 Buscamos si el producto existe en nuestra BD
        for item in carrito_actual:
            if item['id_producto'] == id_prod:
                # Si existe, aumentamos la cantidad y recalculamos el subtotal
                item['cantidad'] += 1

                # Llamamos a la función para calcular el subtotal considerando promociones
                item['subtotal_linea'] = calcular_subtotal(item['cantidad'])

                # buscamos el renglon exacto en la tabla para actualizar
                for child in tree_carrito.get_children():
                    valores_fila = tree_carrito.item(child, "values")
                    if str(valores_fila[0]) == str(id_prod):
                        # Actualizamos la fila mostrando el precio y subtotal correctamente
                        tree_carrito.item(child, values=(
                            id_prod,
                            descripcion,
                            item['cantidad'],
                            f"${precio_unitario:.2f}",
                            f"${item['subtotal_linea']:.2f}"
                            )
                        )
                        break

                actualizar_total_visual()
                return  # Salimos de la función ya que actualizamos el producto existente

        # 2 si el bucle termino y no encontro el producto lo creamos de cero
        subtotal_inicial = calcular_subtotal(1)

        nuevo_item = {
            'id_producto': id_prod,
            'descripcion': descripcion,
            'cantidad': 1,
            'precio_unitario': precio_unitario,
            'subtotal_linea': subtotal_inicial,
            'tipo_linea': 'PRODUCTO'
        }
        carrito_actual.append(nuevo_item)

        # Insertamos el nuevo renglon en el treeview
        tree_carrito.insert('', tk.END, values=(
            id_prod,
            descripcion,
            1,
            f"${precio_unitario:.2f}",
            f"${subtotal_inicial:.2f}"
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

    def procesar_cobro(event=None):
        """
        Controlador: Lee el carrito, valida y abre la vista del modal
        """
        items_carrito = tree_carrito.get_children()
        if not items_carrito:
            messagebox.showwarning("Carrito Vacio", "No hay productos para cobrar")
            return

        carrito_para_bd = []
        total_final = 0.0

        for item in tree_carrito.get_children():
            valores = tree_carrito.item(item)['values']
            codigo = str(valores[0]).strip()
            descripcion = str(valores[1]).strip()
            cantidad = int(valores[2])
            precio = float(str(valores[3]).replace('$', '').strip())
            subtotal = float(str(valores[4]).replace('$', '').strip())

            carrito_para_bd.append({
                'id': codigo,
                'desc': descripcion,
                'cant': cantidad,
                'precio': precio,
                'subtotal': subtotal
            })
            total_final += subtotal

        # --- CALLBACK: Función que el modal llamará al apretar 'Confirmar' ---
        def confirmar_venta_logica(metodo_elegido, monto_recargo, total_calculado):
            exito, mensaje = registrar_venta_transaccion(
                carrito=carrito_para_bd,
                metodo_pago=metodo_elegido,
                subtotal=total_final,
                impuestos=monto_recargo,
                total_final=total_calculado,
                id_usuario=1 
            )

            if exito:
                messagebox.showinfo("Venta Exitosa", mensaje)
                
                # Limpiar la vista principal
                for item in tree_carrito.get_children():
                    tree_carrito.delete(item)
                
                carrito_actual.clear() 
                actualizar_total_visual() 
                entry_busqueda.focus()
                return True # Le avisa al modal que cierre
            else:
                messagebox.showerror("Error", mensaje)
                return False # Le avisa al modal que NO cierre por un error en BD

        # Llamamos a la vista pasando el parent, el subtotal y el callback
        crear_modal_cobro(tree_carrito.winfo_toplevel(), total_final, confirmar_venta_logica)
            
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
    tree_carrito.winfo_toplevel().bind("<F12>", procesar_cobro)

    # Asignacion de Command (clics en los botones)
    boton_cancelar.config(command=cancelar_venta)
    boton_eliminar.config(command=eliminar_item)
    boton_cobrar.config(command=procesar_cobro)