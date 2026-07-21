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
                codigo_barras TEXT PRIMARY KEY,
                id_marca INTEGER NOT NULL,
                id_capacidad INTEGER NOT NULL,
                id_promocion INTEGER,
                precio_compra REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                stock_minimo INTEGER NOT NULL DEFAULT 5,
                estado INTEGER DEFAULT 1,
                FOREIGN KEY(id_marca) REFERENCES marcas(id),
                FOREIGN KEY(id_capacidad) REFERENCES capacidades(id)
                FOREIGN KEY(id_promocion) REFERENCES promociones(id)
            )
    ''')

    # D5 Archivo Venta (cabecera y detalle)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total REAL NO NULL,
                id_usuario INTEGER NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            )
    ''')
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_venta(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                codigo_producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(id_venta) REFERENCES ventas(id),
                FOREIGN KEY(codigo_producto) REFERENCES productos(codigo_barras)
            )
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
