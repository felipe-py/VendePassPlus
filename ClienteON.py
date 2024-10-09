import socket
import json
from models.client.cliente_utils import * 
import time

# O host antigo era 'servidor_container'
HOST = ''
PORT = 65432

def main():
    while True:
        try:
            s1 = conectar(HOST, PORT)
            espacos()
            print("Conectado.")
            espacos()
            break
        except ConnectionRefusedError:
            print(f"A conexão com o servidor {HOST} na porta {PORT} falhou")
            time.sleep(1)

    while True:
        user = login(s1)
        if user == "sair":
            break
        elif user:
            menu(s1, user)
            break
        else:
            print("Credenciais incorretas, tente novamente.")
            espacos()

    # user = login(s1)
    #
    # if user:
    #     menu(s1, user)

main()
