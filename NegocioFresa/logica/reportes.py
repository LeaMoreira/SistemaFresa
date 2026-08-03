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
        condicion_fecha = "AND DATE(v.fecha_hora, 'localtime') = DATE('now', 'localtime')"
    elif filtro == "mes":
        condicion_fecha = "AND strftime('%Y-%m', v.fecha_hora, 'localtime') = strftime('%Y-%m', 'now', 'localtime')"

    query = f'''
        SELECT 
            p.id_producto,
            m.nombre || ' ' || c.litros || 'L' AS descripcion,
            p.precio_compra AS costo_unitario,
            p.precio_venta AS venta_unitaria,
            SUM(dv.cantidad) AS cantidad_vendida,
            SUM(dv.subtotal_linea) AS total_recaudado,
            SUM(dv.cantidad * p.precio_compra) AS costo_total,
            (SUM(dv.subtotal_linea) - SUM(dv.cantidad * p.precio_compra)) AS ganancia_bruta
        FROM detalle_venta dv
        JOIN ventas v ON dv.id_venta = v.id_venta
        JOIN productos p ON dv.id_producto = p.id_producto
        JOIN marcas m ON p.id_marca = m.id
        JOIN capacidades c ON p.id_capacidad = c.id
        WHERE v.estado = 1 {condicion_fecha}
        GROUP BY p.id_producto, descripcion
        ORDER BY ganancia_bruta DESC
    '''
    
    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Totales acumulados del periodo
        total_recaudado = sum(f['total_recaudado'] for f in resultados)
        total_costo = sum(f['costo_total'] for f in resultados)
        total_ganancia = sum(f['ganancia_bruta'] for f in resultados)
        
        return {
            "recaudado": total_recaudado,
            "costo": total_costo,
            "ganancia": total_ganancia,
            "detalle": resultados
        }
    except sqlite3.Error as e:
        print(f"Error al calcular rentabilidad: {e}")
        return {"recaudado": 0, "costo": 0, "ganancia": 0, "detalle": []}
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
