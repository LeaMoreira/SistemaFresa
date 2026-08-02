"""
Modulo de logica para reportes y estadistica
Procesa los datos de ventas e inventario para la toma de decisiones
"""

import sqlite3
from base_datos.conexion import obtener_conexion

def obtener_balance_ventas(filtro="historico"):
    """
    Calcula el total recaudado y lo desglosa pr metodo de pago
    Recibe un filtro: hoy, mes, historico
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Preparamos la peticion de fecha segun lo que pida para ver
    condicion_fecha = ""
    if filtro == "hoy":
        # Compara solo la parte de la fecha YYYY-MM-DD con la fecha actual de local
        condicion_fecha = "AND DATE(fecha_hora, 'localtime') = DATE('now', 'localtime')"
    elif filtro == "mes":
        # Compara solo el mes y año con la fecha actual de local
        condicion_fecha = "AND strftime('%Y-%m', fecha_hora, 'localtime') = strftime('%Y-%m', 'now', 'localtime')"

    query = f'''
        SELECT
            metodo_pago,
            COUNT(id_venta) as cantidad_operaciones,
            COALESCE(SUM(total_final), 0.0) as total_recaudado
        FROM ventas
        WHERE estado = 1 {condicion_fecha}
        GROUP BY metodo_pago
    '''

    try:
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Calculamos el gran total sumamdo los subtotales de cada metodo
        gran_total = sum(fila['total_recaudado'] for fila in resultados)

        return {
            "gran_total": gran_total,
            "desglose": resultados
        }
    except sqlite3.Error as e:
        print(f"ERROR al obtener balance de ventas: {e}")
        return {"gran_total": 0.0, "desglose": []}
    finally:
        conexion.close()

def obtener_productos_mas_vendidos(filtro="historico"):
    """
    Cruza los detalle de ventas con productos para ver la rotacion de inventario
    ordena de mayor amanor la cantidad ventidad
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    condicion_fecha = ""
    if filtro == "hoy":
        condicion_fecha = "AND DATE(v.fecha_hora, 'localtime') = DATE('now', 'localtime')"
    elif filtro == "mes":
        condicion_fecha = "AND strftime('%Y-%m', v.fecha_hora, 'localtime') = strftime('%Y-%m', 'now', 'localtime')"

    query = f'''
        SELECT
            p.id_producto,
            m.nombre || ' ' || c.litros || 'L' AS descripcion_producto,
            SUM(dv.cantidad) AS total_unidades_vendidas,
            SUM(dv.subtotal_linea) AS recaudacion_total
        FROM detalle_venta dv
        JOIN ventas v ON dv.id_venta = v.id_venta
        JOIN productos p ON dv.id_producto = p.id_producto
        JOIN marcas m ON p.id_marca = m.id
        JOIN capacidades c ON p.id_capacidad = c.id
        WHERE v.estado = 1 {condicion_fecha}
        GROUP BY p.id_producto, descripcion_producto
        ORDER BY total_unidades_vendidas DESC
    '''

    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"ERROR al obtener productos mas vendidos: {e}")
        return []
    finally:
        conexion.close()

def obtener_estado_inventario():
    """
    Trae todo el stock actual y sus limites
    Ideal para el sistema de alerta visuales tipo semaforo
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute('''
            SELECT
                p.id_producto,
                m.nombre || ' ' || c.litros || 'L' AS descripcion,
                p.stock_actual,
                p.stock_minimo
            FROM productos p
            JOIN marcas m ON p.id_marca = m.id
            JOIN capacidades c ON p.id_capacidad = c.id
            WHERE p.estado = 1
            ORDER BY p.stock_actual ASC
        ''')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"ERROR al obtener estado de inventario: {e}")
        return []
    finally:
        conexion.close()
