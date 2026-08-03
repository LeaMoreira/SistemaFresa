"""
modulo raiz del sistema
"""
from base_datos.conexion import inicializar_base_datos
from vistas.login import mostrar_login

def main():
    # 1 BOOSTRAP DE DATOS: verificamos y creamos la base de datos AppData
    print("Inicializando base de datos y sistema")
    inicializar_base_datos()

    # 2 CEDE CONTROL: llamamos al modulo que maneja tkinter
    print("Iniciando interfaz de usuario")
    mostrar_login()

if __name__ == "__main__":
    main()
