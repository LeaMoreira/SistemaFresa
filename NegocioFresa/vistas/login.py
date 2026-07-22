"""
modulo vista para login de usuario
"""

import tkinter as tk
from tkinter import messagebox
from logica.auth import validar_credenciales

def iniciar_sesion(ventana_login, entry_usuario, entry_password):
    """
    Captura los datos de interfaz, llama a la logica de negocio y
    decide que mensaje mostrarle al usuario
    """

    usuario = entry_usuario.get()
    password = entry_password.get()

    # validacion basica de interfaz
    if not usuario or not password:
        messagebox.showwarning("Atencion", "Por favor, complete todos los campos")
        return
    
    # llamamos a nuestro modulo de logica (proceso 1 del DFD)
    resultado = validar_credenciales(usuario, password)

    if resultado:
        messagebox.showinfo("Exito", "Inicio de sesion exitoso")
        # si el login es correcto, destruimos la ventana para luego abrir el menu principal
        ventana_login.destroy()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos o usuario inactivo")

def mostrar_login():
    """
    Renderizamos la ventana de inicio de sesion
    """

    ventana = tk.Tk()
    ventana.title("Negocio Fresa - Login")
    # Ancho x Alto y evitamos que el usuario cambie el tamaño de la ventana
    ventana.geometry("300x250")
    ventana.resizable(False, False)

    # Un marco principal para darle margenes ordenados a los elementos
    marco = tk.Frame(ventana, padx=20, pady=20)
    marco.pack(expand=True, fill=tk.BOTH)

    # Titulo
    tk.Label(marco, text="Iniciar Sesion", font=("Arial", 14, "bold")).pack(pady=(0,15))

    # Campo de Usuario
    tk.Label(marco, text="Usuario:").pack(anchor="w")
    # El atributo 'show' es clave para enmascarar la contraseña
    entry_usuario = tk.Entry(marco, width=30)
    entry_usuario.pack(pady=(0,10))

    tk.Label(marco, text="Contraseña:").pack(anchor="w")
    entry_password = tk.Entry(marco, width=30, show="*")
    entry_password.pack(pady=(0,10))
    
    boton_ingresar = tk.Button(marco, text="Ingresar", command=lambda: iniciar_sesion(ventana, entry_usuario, entry_password),
                        bg="#ff4d4d", fg="white", font=("Arial", 10, "bold")
    )
    boton_ingresar.pack(fill=tk.X)

    # Bucle principal para mantener la ventana abierta
    ventana.mainloop()
