"""
client.py
==========

Cliente para control remoto basado en Python.

Autor: David Duran <david@devduran.com>
Fecha: 10 de junio de 2023
Repositorio: https://github.com/ddevduran/py-remote-control.git

"""

import socket
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ssl

# Direción y puerto
HOST = '0.0.0.0'
PORT = 1337

# Usuario y contraseña para autenticación
USER = 'admin'
PASSWORD = 'admin'

def receive_file(s, filename):
    """Recibe un archivo del servidor."""
    with open(filename, 'wb') as file:
        while True:
            data = s.recv(1024)
            if not data:
                break
            file.write(data)

def send_file(s, filename, destination):
    """Envía un archivo al servidor."""
    s.send(f'upload {destination}'.encode('utf-8'))
    s.recv(1024)  # Receive acknowledgment

    with open(filename, 'rb') as file:
        for data in file:
            s.sendall(data)

def on_send_button(event=None):
    """Función que se ejecuta cuando se pulsa el botón de enviar."""
    command = command_entry.get()
    if not command:
        messagebox.showwarning("Comando vacío", "Por favor, ingrese un comando.")
        return

    if command == 'q':
        root.quit()
        return

    if command.startswith('upload '):
        filename = command[7:]
        if os.path.exists(filename):
            destination = filedialog.askdirectory()
            if destination:
                messagebox.showinfo("Envío de archivo", f"Cargando archivo {filename}...")
                send_file(s, filename, destination)
                messagebox.showinfo("Envío de archivo", f"Archivo {filename} enviado correctamente")
            else:
                messagebox.showwarning("Envío de archivo", "No se seleccionó un destino en el servidor")
        else:
            messagebox.showerror("Envío de archivo", f"Archivo {filename} no encontrado")
    elif command.startswith('download '):
        filename = command[9:]
        messagebox.showinfo("Descarga de archivo", f"Descargando archivo {filename}...")
        receive_file(s, filename)
        messagebox.showinfo("Descarga de archivo", f"Archivo {filename} recibido correctamente")
    else:
        s.send(command.encode('utf-8'))

        output = s.recv(1024)
        if output == b'':
            root.quit()
            return

        if output == b'CLEAR_SCREEN_COMMAND':
            output_text.delete('1.0', tk.END)
        else:
            output_text.insert(tk.END, output.decode('utf-8'))

    command_entry.delete(0, tk.END)

def browse_file():
    """Permite al usuario seleccionar un archivo para cargar."""
    filename = filedialog.askopenfilename()
    command_entry.insert(tk.END, f'upload {filename}')

def configure_window(event=None):
    """Configura la ventana para adaptarse a su contenido."""
    output_text.configure(width=output_frame.winfo_width() // 10, height=output_frame.winfo_height() // 25)

def create_ui():
    """Crea la interfaz de usuario."""
    global root, command_entry, output_text, s

    root = tk.Tk()
    root.title("Cliente de Control Remoto")

    # Configuración de estilos
    bg_color = "#333333"
    fg_color = "#333333"
    entry_bg_color = "#ffffff"
    button_bg_color = "#ff0000"
    button_fg_color = "#000000"

    # Frame principal
    main_frame = tk.Frame(root, padx=20, pady=20, bg=bg_color)
    main_frame.pack(fill='both', expand=True)

    # Etiqueta de comando
    command_label = tk.Label(main_frame, text="Comando:", bg=bg_color, fg="#ffffff")
    command_label.grid(row=0, column=0, sticky='W')

    # Entrada de comando
    command_entry = tk.Entry(main_frame, width=50, bg=entry_bg_color, fg=fg_color)
    command_entry.grid(row=0, column=1, padx=10, pady=5)

    # Botón de selección de archivo
    browse_button = tk.Button(main_frame, text="Seleccionar archivo", command=browse_file, width=15, bg=button_bg_color, fg=button_fg_color)
    browse_button.grid(row=1, column=1, pady=10, sticky='E')


    # Botón de enviar
    send_button = tk.Button(main_frame, text="Enviar", command=on_send_button, width=10, bg=button_bg_color, fg=button_fg_color)
    send_button.grid(row=0, column=2, padx=5, pady=5)
    
    # Frame de salida
    global output_frame
    output_frame = tk.Frame(root, bg=bg_color)
    output_frame.pack(fill='both', expand=True)

    # Área de texto de salida
    output_text = tk.Text(output_frame, bg=entry_bg_color, fg=fg_color)
    output_text.pack(fill='both', expand=True)

    # Configurar redimensionamiento de ventana
    root.bind("<Configure>", configure_window)

    s = socket.socket()
    s = ssl.wrap_socket(s)
    s.connect((HOST, PORT))

    s.send(USER.encode('utf-8'))
    s.send(PASSWORD.encode('utf-8'))
    auth_status = s.recv(1024).decode('utf-8')

    if auth_status == 'AUTH_FAILED':
        messagebox.showerror("Error de autenticación", "Usuario o contraseña incorrectos.")
        s.close()
        root.quit()
        return

    root.bind('<Return>', on_send_button)
    root.mainloop()

    s.close()

def main():
    """Función principal que crea la interfaz de usuario."""
    create_ui()

if __name__ == '__main__':
    main()
