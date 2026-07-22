"""
DFD proceso 2.1 y 2.2
se conectan con la base de datos y convertirmos los datos en diccionarios de python
usamos para cargar los datos en la interfaz de usuario
"""

import sqlite3
from base_datos.conexion import obtener_conexion

# --- PROCESO 2: Gestionar Parametros (Marcas y Capacidades) --- #

def registrar_marca(nombre_marca):
    """
    P2.2 Guardamos una nueva marca en el D2 Archivo Parametro
    returna True o False dependiendo si se pudo guardar o no
    """

    conexcion = obtener_conexion()
    cursor = conexcion.cursor()

    try:
        # Usamos los Strip() para quietar espacion extra y upper() para estandarizar datos
        nombre_limpio = nombre_marca.strip().upper()
        cursor.execute("INSERT INTO marcas (nombre) VALUES (?)", (nombre_limpio,))
        conexcion.commit()
        return True
    except sqlite3.IntegrityError:
        # Se activa si intentamos cargar una marca que ya existe (UNIQUE constraint)
        return False
    finally:
        conexcion.close()

def listar_marcas():
    """
    P2.1 Consultamos las marcas activas en D" para llenar los desplegables 
    Solo trae aquellas con estado = 1 (RF 5)
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre FROM marcas WHERE estado = 1 ORDER BY nombre ASC")
    # Formateamos la respuesta como una lista de diccionarios (Patron Factory adaptado)
    resultado = [dict(fila) for fila in cursor.fetchall()]

    conexion.close()
    return resultado

def registrar_capacidad(litros):
    """
    P2.2 Guarda una nueva capacidad (ejemplo 1.0, 1.5) en el D2
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Aseguramos que el valor de litros sea numeros decimal (float)
        valor_litros = float(litros)
        cursor.execute("INSERT INTO capacidades (litros) VALUES (?)", (valor_litros,))
        conexion.commit()
        return True
    except (sqlite3.IntegrityError, ValueError):
        return False
    finally:
        conexion.close()

def listar_capacidades():
    """
    P2.1 Consultamos las capacidades activas en D" para llenar los desplegables
    Solo trae aquellas con estado = 1 (RF 5)
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, litros FROM capacidades WHERE estado = 1 ORDER BY litros ASC")
    resultado = [dict(fila)for fila in cursor.fetchall()]

    conexion.close()
    return resultado

# Proceso 3 - Gestionar Producto
def registrar_producto(id_producto, id_marca, id_capacidad, precio_compra, precio_venta, stock_actual, stock_minimo):
    """
    P3.1 Da alta un nuevo producto a D3 Archivo Producto
    Soporta lector ID manual o escaneado por codigo de barras en RF 4
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # limpiamos el ID por si la lectura introduce espacios
        id_limpio = str(id_producto).strip()

        cursor.execute("""
            INSERT INTO productos (
                id_producto, id_marca, id_capacidad,
                precio_compra, precio_venta, stock_actual, stock_minimo, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (id_limpio, int(id_marca), int(id_capacidad),
              float(precio_compra), float(precio_venta),
              int(stock_actual), int(stock_minimo)
              )
        )

        conexion.commit()
        return True, "Producto registrado exitosamente"
    except sqlite3.IntegrityError:
        return False, "Error: El codigo/ID de producto ya existe en la base de datos"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
    finally:
        conexion.close()

def listar_producto():
    """
    P3.1 Consulta los productos activos uniendo los datos de Parametros (D2) y productos (D3)
    Aplica baja logica en RF 5: estado = 1
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Hacemos un JOIN para mostrar los nombres de marcas litros juntos con los IDs
    query = """
        SELECT
            p.id_producto,
            m.nombre AS marca,
            c.litros AS capacidad,
            p.precio_compra,
            p.precio_venta,
            p.stock_actual,
            p.stock_minimo
        FROM productos p
        INNER JOIN marcas m ON p.id_marca = m.id
        INNER JOIN capacidades c ON p.id_capacidad = c.id
        WHERE p.estado = 1
        ORDER BY m.nombre ASC
    """

    cursor.execute(query)
    resultados = [dict(fila) for fila in cursor.fetchall()]

    conexion.close()
    return resultados

def modificar_precio_y_stock(id_producto, nuevo_precio_compra, nuevo_precio_venta, stock_reposicion):
    """
    P3.2 / RF6 y RF7 Modificar precios de compra/venta de forma independiente
    y permite reponer stock sumando la cantidad ingresada al inventario actual
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        query = """
            UPDATE productos
            SET precio_compra = ?,
                precio_venta = ?,
                stock_actual = stock_acutal + ?
            WHERE id_productos = ? AND estado = 1
        """

        cursor.execute(query, (
            float(nuevo_precio_compra),
            float(nuevo_precio_venta),
            int(stock_reposicion),
            str(id_producto)
            )
        )

        conexion.commit()
        return True, "Producto actualizado correctamente"
    except Exception as e:
        return False, f"Error al alcuatlizar producto: {str(e)}"
    finally:
        conexion.close()

def dar_baja_logica_producto(id_producto):
    """
    RF5 Realiza la baja logica cambiando el estado a 0 (No hay borrado fisico)
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("UPDATE productos SET estado = 0 WHERE id_producto = ?", (str(id_producto),))
        conexion.commit()
        return True, "Producto dado de baja con exito"
    except Exception as e:
        return False, f"Error al dar de baja: {str(e)}"
    finally:
        conexion.close()

def reactivar_producto(id_producto):
    """
    Revierte la baja logica cambiado el estado del producto
    0 a 1
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("UPDATE productos SET estado = 1 WHERE id_producto = ?", (str(id_producto),))
        conexion.commit()
        return True, "Producto reactivado con exito"
    except Exception as e:
        return False, f"Error al reactivar: {str(e)}"
    finally:
        conexion.close()

def verificar_estado_producto(id_producto):
    """
    Consulta si un producto existe en la base de datos
    Retorna 1 (activo), 0 (inactivo) o None (no existe)
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT estado FROM productos WHERE id_productos = ?", (str(id_producto).strip(),))
    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        # dict(resultado) convierte la fila de SQLite para acceder por clave
        return dict(resultado)['estado']
    return None

def reactivar_producto_individual(id_producto, nuevo_stock):
    """
    Revierte la baja de un producto y le asigna el nuevo stock ingresado
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "UPDATE productos SET estado = 1, stock_actual = ? WHERE id_producto = ?",
            (int(nuevo_stock), str(id_producto).strip())
        )
        conexion.commit()
        return True
    except Exception:
        return False
    finally:
        conexion.close()

def reactivar_todos_los_productos():
    """
    Solo para Pruebas:
        Pasa todos los productos con baja logica (0) a activos (1)
        retorna la cantidad de filas afectadas
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("UPDATE productos SET estado = 1 WHERE estado = 0")
        filas_afectadas = cursor.rowcount
        conexion.commit()
        return filas_afectadas
    except Exception:
        return 0 
    finally:
        conexion.close()
