"""
Logica de promociones para agrupar productos
"""

import sqlite3
from base_datos.conexion import obtener_conexion

def obtener_todas_promociones():
    """
    Trae TODAS las promociones (activas e inactivas)
    y busca el nombre del producto asociado para mostrarlo en pantalla
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Le sacamos el "WHERE p.estado = 1" y sumamos "p.estado" al SELECT
        cursor.execute('''
                SELECT
                    p.id,
                    p.nombre AS nombre_promo,
                    p.id_producto,
                    m.nombre || ' ' || c.litros || 'L' AS descripcion_producto,
                    p.cantidad_requerida,
                    p.precio_promo,
                    p.estado
                FROM promociones p
                JOIN productos pr ON p.id_producto = pr.id_producto
                JOIN marcas m ON pr.id_marca = m.id
                JOIN capacidades c ON pr.id_capacidad = c.id
        ''')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"ERROR al obtener promociones: {e}")
        return []
    finally:
        conexion.close()

def cambiar_estado_promocion_bd(id_promo, nuevo_estado):
    """
    Actualiza el estado de la promoción (0 = Baja, 1 = Alta)
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute('''UPDATE promociones
                       SET estado = ?
                       WHERE id = ?''',
                       (nuevo_estado, id_promo))
        conexion.commit()
        accion = "dada de alta" if nuevo_estado == 1 else "dada de baja"
        return True, f"Promoción {accion} correctamente."
    except sqlite3.Error as e:
        conexion.rollback()
        return False, f"ERROR al cambiar estado: {e}"
    finally:
        conexion.close()

def agregar_promocion(nombre, id_producto, cantidad, precio):
    """
    Inserta una nueva promocion en la base de datos
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute('''
                INSERT INTO promociones (nombre, id_producto, cantidad_requerida,
                precio_promo, estado)
                VALUES (?, ?, ?, ?, 1)
        ''', (nombre, id_producto, cantidad, precio))
        conexion.commit()
        return True, "Promocion creada correctamente"
    except sqlite3.IntegrityError:
        conexion.rollback()
        return False, "Ya existe una promocion con ese nombre"
    except sqlite3.Error as e:
        conexion.rollback()
        return False, f"ERROR en la BD: {e}"
    finally:
        conexion.close()

def actualizar_promocion(id_promo, nueva_cantidad, nuevo_precio):
    """
    Actualizamos la unidades requeridas y el precio existente
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute('''
                UPDATE promociones
                SET cantidad_requerida = ?, precio_promo = ?
                WHERE id = ? AND estado = 1
        ''', (nueva_cantidad, nuevo_precio, id_promo))
        conexion.commit()
        return True, "Promocion actualizada correctamente"
    except sqlite3.Error as e:
        conexion.rollback()
        return False, f"ERROR al actualizar promocion: {e}"
    finally:
        conexion.close()
