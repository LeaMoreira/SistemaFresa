"""
la conexion con el squlite3
y sus interacciones
"""

import sqlite3
import os
import hashlib

# Definimos la ruta absoluta para que SQLite no cree el archivo en otro lado por error
DIRECTORIO_ACTUAL = os.path.dirname(__file__)
RUTA_BD = os.path.join(DIRECTORIO_ACTUAL, 'negocio_fresa.db')

def obtener_conexion():
    """
    Adaptacion del patron Singleton:
    Retorna una conexion activa a SQLite configurada para trabajar con diccionarios.
    """
    conexion = sqlite3.connect(RUTA_BD)
    # esto nos permite acceder a las columnas por su nombre (ejemplo: fila['precio'])
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_base_datos():
    """
    Crea todas las tablas (D1 a D5) siguiendo el DER y el balanceo de flujos
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # D1: Archivo Usuario
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   usuario TEXT UNIQUE NOT NULL,
                   password_hash TEXT NOT NULL,
                   estado INTEGER DEFAULT 1
            )
    ''')

    # D2 Archivo Parametro (Marcas y Capacidades)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS marcas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                estado INTEGER DEFAULT 1
            )
    ''')
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS capacidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                litros REAL NOT NULL,
                estado INTEGER DEFAULT 1
            )
    ''')

    # D4 Archivo Promocion
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS promociones(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descuento REAL DEFAULT 0,
                estado INTEGER DEFAULT 1
            )
    ''')

    # D3 Archivo Producto (el nucleo del inventario)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos(
                id_producto TEXT PRIMARY KEY,
                id_marca INTEGER,
                id_capacidad INTEGER,
                precio_compra REAL,
                precio_venta REAL,
                stock_actual INTEGER,
                stock_minimo INTEGER,
                estado INTEGER DEFAULT 1,
                FOREIGN KEY(id_marca) REFERENCES marcas(id),
                FOREIGN KEY(id_capacidad) REFERENCES capacidades (id)
            );
    ''')
    # TABLA DE VENTAS (CORREGIDAD)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                metodo_pago TEXT NOT NULL,
                subtotal REAL NOT NULL,
                impuestos_comisiones REAL DEFAULT 0.0,
                total_final REAL NOT NULL,
                id_usuario INTEGER DEFAULT 1,
                estado INTEGER DEFAULT 1,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            );
    ''')
    # DETALLE DE VENTAS (CORREGIDA)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                id_producto TEXT,
                descripcion_linea TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal_linea REAL NOT NULL,
                tipo_linea TEXT DEFAULT 'PRODUCTO',
                FOREIGN KEY(id_venta) REFERENCES ventas(id_venta),
                FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
            );
    ''')

    # INYECCION DE ADMINISTRADOR INICIAL RF-1
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'root'")
    if not cursor.fetchone():
        # encriptamos la contraseña con SHA-256 nativo de python
        password_hash = hashlib.sha256('Gamblers120693'.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)",
            ('root', password_hash)
        )

    conexion.commit()
    conexion.close()
    print("Base de datos y tablas iniciadas con exito")

# Este bloque ejecutra el archivo directamente para crear el BD
if __name__ == '__main__':
    inicializar_base_datos()
