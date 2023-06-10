# Python Remote Control

Este proyecto proporciona una solución simple y eficaz para el control remoto de sistemas utilizando Python. Consiste en dos scripts principales, `client.py` y `server.py`, que se comunican entre sí a través de un protocolo de conexión segura.

## Autor

David Duran <david@devduran.com>

## Repositorio

https://github.com/ddevduran/py-remote-control.git

## Dependencias

Este proyecto depende de los siguientes paquetes de Python:

- tkinter
- socket
- os
- ssl

Puedes instalar estas dependencias con pip:
pip3 install tk

## Uso

1. Ejecuta el script `server.py` en el servidor que deseas controlar (python3 server.py).

2. Ejecuta el script `client.py` en el cliente que se utilizará para controlar el servidor (python3 client.py).

3. En el cliente, puedes introducir comandos en el cuadro de texto. Los comandos se envían al servidor para su ejecución cuando haces clic en el botón "Enviar".

## Características

- Soporta la subida y bajada de archivos entre el cliente y el servidor.
- Conexión segura SSL para proteger la transmisión de datos.
- Autenticación para proteger el acceso al servidor.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.
