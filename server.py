"""
server.py
==========

Servidor para control remoto basado en Python.

Autor: David Duran <david@devduran.com>
Fecha: 10 de junio de 2023
Repositorio: https://github.com/ddevduran/py-remote-control.git

"""

import socket
import subprocess
import os
import ssl
from rich import print
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Direción y puerto
HOST = '0.0.0.0'
PORT = 1337

# Usuario y contraseña para autenticación
USER = 'admin'
PASSWORD = 'admin'

def receive_file(conn, filename):
    """Recibe un archivo del cliente."""
    with open(filename, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)

def send_file(conn, filename):
    """Envía un archivo al cliente."""
    with open(filename, 'rb') as file:
        for data in file:
            conn.sendall(data)

def get_running_processes():
    """Obtiene los procesos en ejecución dependiendo del sistema operativo."""
    if os.name == 'posix':  # Unix/Linux/MacOS
        cmd = "ps aux"
    elif os.name == 'nt':  # Windows
        cmd = "tasklist"
    else:
        return "No se puede obtener información de procesos en este sistema"

    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        output = f'Error: {e.stderr}'

    return output

def kill_process(process_id):
    """Mata un proceso por su ID dependiendo del sistema operativo."""
    if os.name == 'posix':  # Unix/Linux/MacOS
        cmd = f"kill -9 {process_id}"
    elif os.name == 'nt':  # Windows
        cmd = f"taskkill /F /PID {process_id}"
    else:
        return "No se puede matar el proceso en este sistema"

    try:
        subprocess.check_output(cmd, shell=True)
        return "Proceso terminado exitosamente"
    except subprocess.CalledProcessError as e:
        return f'Error al terminar el proceso: {e.stderr}'

def delete_file_or_directory(path):
    """Elimina un archivo o directorio."""
    if os.path.isfile(path):
        confirm = Prompt.ask(f"¿Estás seguro de que deseas eliminar el archivo '{path}'? (y/n)", choices=['y', 'n'])
        if confirm == 'y':
            try:
                os.remove(path)
                return f'Archivo {path} eliminado exitosamente'
            except Exception as e:
                return f'Error al eliminar el archivo {path}: {str(e)}'
        else:
            return 'Eliminación de archivo cancelada'
    elif os.path.isdir(path):
        confirm = Prompt.ask(f"¿Estás seguro de que deseas eliminar el directorio '{path}' y su contenido? (y/n)", choices=['y', 'n'])
        if confirm == 'y':
            try:
                os.rmdir(path)
                return f'Directorio {path} eliminado exitosamente'
            except Exception as e:
                return f'Error al eliminar el directorio {path}: {str(e)}'
        else:
            return 'Eliminación de directorio cancelada'
    else:
        return f'{path} no existe o no es un archivo/directorio válido'

def main():
    """Función principal que inicia el servidor."""
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(1)
    print('[INFO] Escuchando en el puerto 1337...')
    conn, addr = s.accept()
    print(f'[INFO] Conexión establecida con {addr}')

    # Crear un nuevo contexto SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # Cargar la clave y el certificado
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    # Usar el contexto para envolver el socket
    conn = context.wrap_socket(conn, server_side=True)


    user = conn.recv(1024).decode('utf-8')
    password = conn.recv(1024).decode('utf-8')

    if user == USER and password == PASSWORD:
        conn.send('AUTH_SUCCESSFUL'.encode('utf-8'))
    else:
        conn.send('AUTH_FAILED'.encode('utf-8'))
        conn.close()
        print(f'[INFO] Conexión cerrada con {addr}')
        return

    while True:
        command = conn.recv(1024).decode('utf-8')
        if not command:
            break

        print(f'[COMMAND] {command}')

        if command.startswith('upload '):
            filename = command[7:]
            receive_file(conn, filename)
        elif command.startswith('download '):
            filename = command[9:]
            send_file(conn, filename)
        elif command == 'q':
            conn.send(b'')
            break
        elif command == 'getproc':
            output = get_running_processes()
            conn.send(output.encode('utf-8'))
        elif command.startswith('killproc '):
            process_id = command[9:]
            output = kill_process(process_id)
            conn.send(output.encode('utf-8'))
        elif command.startswith('delete '):
            path = command[7:]
            output = delete_file_or_directory(path)
            conn.send(output.encode('utf-8'))
        else:
            output = subprocess.check_output(command, shell=True, text=True)
            conn.send(output.encode('utf-8'))

    conn.close()
    print(f'[INFO] Conexión cerrada con {addr}')

if __name__ == '__main__':
    main()
