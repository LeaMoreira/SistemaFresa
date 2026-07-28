"""
Modulo logico de ventas para manejar las transacciones correctamente
"""

import sqlite3
from base_datos.conexion import obtener_conexion

def registrar_transaccion_venta(id_usuario, metodo_pago, subtotal, impuesto, total_final, carrito):
    """
    Registramos la cabecera, el detalle y descuento el stock en uan sola transaccion
    El carrito debe ser uan lista de diccionario con la estrutura del detalle
    Retorna (true por id_venta) si fue exitoso o (false, mensaje_error) si fallo
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # 1 insertar Cabezera de venta
        cursor.execute('''
            INSERT INTO ventas (metodo_pago, subtotal, impuesto_comisiones, total_final, id_usuario, estado)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (metodo_pago, float(subtotal), float(impuesto), float(total_final), int(id_usuario))
        )

        # obtenemos el ID de la venta que SQLite nos genera automaticamente
        id_venta = cursor.lastrowid

        # 2 Iteramos sobre cada item del carrito para guardar el detalle y descontar stock
        for item in carrito:
            # Insertamos detalle_venta
            cursor.execute('''
                INSERT INTO detalle_ventas
                (id_venta, id_producto, descripcion_linea, cantidad, precio_unitario, subtotal_linea, tipo_linea)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_venta,
                item.get('id_producto'),
                item['descripcion'],
                int(item['cantidad']),
                float(item['precio_unitario']),
                float(item['subtotal_linea']),
                item.get('tipo_linea', 'PRODUCTO')
                )
            )

            # 3 Descontar Stock (solo si es un producto fisico, ignoranmos descuentos o recargos)
            if item.get('tipo_linea', 'PRODUCTO') == 'PRODUCTO' and item.get('id_producto'):
                cursor.execute('''
                    UPDATE productos
                    SET stock_actual = stock_actual - ?
                    WHERE id_producto = ?
                ''', (int(item['cantidad']), item['id_producto'])
                )

        # 4 Si todo los bucles termina sin errores, confirmamos los cambios en la BD
        conexion.commit()
        return True, id_venta

    except sqlite3.Error as e:
        # Si algo falla en cualquier punto, deshacemos todo lo que se hizo
        conexion.rollback()
        return False, f"ERROR de base de datos al registrar venta: {str(e)}"
    except Exception as e:
        conexion.rollback()
        return False, f"ERROR inesperado al registrar venta: {str(e)}"
    finally:
        conexion.close()