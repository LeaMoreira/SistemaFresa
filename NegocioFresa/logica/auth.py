"""
modulo para la autenticacion de usuarios
"""

import hashlib
from base_datos.conexion import obtener_conexion

def validar_credenciales(usuario, password):
    """
    Verifica si el usuario y la contraseña coinciden con los registros de la BD
    Retorna los datos del usuario (id, usuario) si es correcto, si no, falla
    """

    # 1 encriptamos la contraseña que se tipea por el usuario usuario
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # 2 Abre la conexion a nuestra base de datos SQLite
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 3 Consultamos si existe ese usuario con esa clave exacta y que no este dado de baja
    cursor.execute("SELECT id, usuario FROM usuarios WHERE usuario = ? AND password_hash = ? AND estado = 1",
                   (usuario, password_hash)
    )

    usuario_encontrado = cursor.fetchone()
    conexion.close()
    # cerramos las conexiones para ahorrar memoria

    # 4 Evaluamos el resultado
    if usuario_encontrado:
        # convertimos el resultado a un diccionario para que sea facil leer
        return dict(usuario_encontrado)
    else:
        # si no coincide o esta dado de baja, retornamos None
        return None
