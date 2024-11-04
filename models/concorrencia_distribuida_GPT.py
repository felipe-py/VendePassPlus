# concorrencia_distribuida.py
import socket
import json
import threading
import time
from typing import List, Dict, Tuple, Optional

class Server:
    def __init__(self, id_server, servers):
        self.id_server = id_server
        self.servers = servers
        self.mutex = threading.Lock()
        self.fila = []                  # Fila de pedidos de acesso
        self.relogio = 0                # Relógio lógico de Lamport
        self.ok = False                 # Indica se o acesso foi concedido
        self.contador = 0               # Contador de respostas recebidas
        self.ligado = True               # Indica se o server está ligado
        self.server_connections: Dict[int, Optional[socket.socket]] = {} 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(servers[id_server])
        self.server_socket.listen()

    def conectar_nos_outros_servidores(self):
        while self.ligado:
            for i, (host, port) in enumerate(self.servers):
                if i != self.server_id and i not in self.server_connections:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((host, port))
                        self.server_connections[i] = sock
                        print(f"Conectado ao servidor {i}")
                        # Inicia thread para receber mensagens deste servidor
                        threading.Thread(target=self.handle_server_messages, args=(sock, i)).start()
                    except:
                        print(f"Não foi possível conectar ao servidor {i}")
            time.sleep(3)  # Tenta reconectar a cada 3 segundos

    def incrementar_relogio(self):
        with self.mutex:
            self.relogio += 1

    def pedir_acesso(self):
        self.incrementar_relogio()
        mensagem = {
            "operacao": "pedido_de_acesso",
            "id_server": self.id_server,
            "relogio": self.relogio
        }
        self.contador = 0
        self.ok = False
        
        # Enviar pedido de acesso para todos os outros servidores
        for i in range(len(self.servers)):
            if i != self.id_server:
                self.enviar(i, mensagem)

        # Espera pelas respostas de todos os outros servidores
        while not self.ok:
            time.sleep(0.1)

    def liberar_acesso(self):
        mensagem = {
            "operacao": "liberar_acesso",
            "id_server": self.id_server
        }
        # Envia mensagens de liberação para todos os servidores
        for i in range(len(self.servers)):
            if i != self.id_server:
                self.enviar(i, mensagem)

    def enviar(self, servidor, mensagem):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.servers[servidor])
            s.sendall(json.dumps(mensagem).encode())

    def processar_mensagem(self, mensagem):
        with self.mutex:
            self.relogio = max(self.relogio, mensagem["relogio"]) + 1
            
            if mensagem["operacao"] == "pedido_de_acesso":
                if self.ok or (self.relogio, self.id_server) < (mensagem["relogio"], mensagem["id_server"]):
                    self.enviar(mensagem["id_server"], {
                        "operacao": "resposta",
                        "id_server": self.id_server
                    })
                else:
                    self.fila.append(mensagem)
            elif mensagem["operacao"] == "liberar_acesso":
                self.fila = [req for req in self.fila if req["id_server"] != mensagem["id_server"]]
                if self.fila:
                    proximo = self.fila.pop(0)
                    self.ok = True
                    self.enviar(proximo["id_server"], {
                        "operacao": "resposta",
                        "id_server": self.id_server
                    })

    def handle_request(self, conn):
        mensagem = json.loads(conn.recv(1024).decode())
        conn.close()
        self.processar_mensagem(mensagem)

    def executar(self):
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_request, args=(conn,)).start()

