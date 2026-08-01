"""
Modulo logico de ventas para manejar las transacciones correctamente
"""

import sqlite3
from base_datos.conexion import obtener_conexion

def registrar_venta_transaccion(carrito, metodo_pago, subtotal, impuestos,  total_final, id_usuario=1):
    """
    P4.1 - Registrar cabecera, el detalle y descuento de stock en una sola transaccion ACID
        param carrito: Lista diccionario
        param metodo_pago: String (efectivo, mercadopago, tarjeta)
        param subtotal: Float (suma de los productos)
        param impuestos: Float (recargos o descuentos globales)
        param total_final: Float (lo que paga el cliente)
        param id_usuario: ID del cajero activo 'por defecto es 1 = root'
        return: (True, id_venta) si fue exitoso, o (False, mensaje_error) si fallo
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # 1 Insertamos la cabecera del ticket en venta
        cursor.execute('''
            INSERT INTO ventas (metodo_pago, subtotal, impuestos_comisiones,
                        total_final, id_usuario)
            VALUES (?, ?, ?, ?, ?)
        ''', (metodo_pago, float(subtotal), float(impuestos), float(total_final), int(id_usuario))
        )

        # obtener ID ticket que SQLite acaba de generar
        id_venta = cursor.lastrowid

        # 2 Recorremos el carrito para guardar los detalles y descontar stock
        for item in carrito:
            # Insertamos el detalle
            cursor.execute('''
                INSERT INTO detalle_venta (id_venta, id_producto, descripcion_linea,
                            cantidad, precio_unitario, subtotal_linea)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                id_venta,
                item['id'],
                item['desc'],
                int(item['cant']),
                float(item['precio']),
                float(item['subtotal'])
            ))

            # 3 Descontamos el stock en la tabla de producto
            cursor.execute('''
                UPDATE productos
                SET stock_actual = stock_actual - ?
                WHERE id_producto = ?
            ''', (int(item['cant']), item['id']))

        # 4 si el bucle termina sin errores, sellamos la transaccion
        conexion.commit()
        return True, f"Venta #{id_venta} registrada con exito"
    except Exception as e:
        # Si algo fallta deshacemos todo el cambio en el bloque, rollback
        conexion.rollback()
        return False, f"ERROR al procesar el cobro {str(e)}"

    finally:
        conexion.close()
