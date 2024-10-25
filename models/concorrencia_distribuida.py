import socket
import json
import threading
import time

#Algortimo de Ricart-Agrawala.
class Server:
    def __init__(self, id_server, servers):
        self.id_server = id_server      # Identificador do servidor para saber a qual servidor esta se referindo (A, B ou C)
        self.servers = servers          # Lista de endereços dos outros servidores
        self.mutex = threading.Lock()   # Mutex para proteger variáveis compartilhadas
        self.fila = []                  # Fila de pedidos de acesso
        self.relogio = 0                # Relógio lógico
        self.ok = False                 # Indica se o acesso foi concedido
        self.contador = 0               # Contador de respostas recebidas
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(servers[id])
        self.server_socket.listen()

    def pedir_acesso(self):
        self.relogio += 1  
        mensagem = {
            "operacao": "pedido_de_acesso", #Poderia ser opcode como no servidor, mas eu deixei operação aqui, pra facilitar a leitura/escrita do codigo
            "id_server": self.id_server,
            "relogio": self.relogio
        }
        self.contador = 0
        self.ok = False
        
        # Enviar pedido de acesso para todos os outros servidores
        for i in range(len(self.servers)):
            if i != self.id_server:
                self.enviar(i, mensagem)

        # Espera pelas respostas
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

    # Essa função aqui faz a mesma coisa que enviar mensagem, mas sem opcode
    def enviar(self, servidor, mensagem):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.servers[servidor])
            s.sendall(json.dumps(mensagem).encode())

    # Essa função só está aqui pra garantir que a mensagem que chegou foi do tipo esperado, não deveria dar problema em momento nenhum, mas é melhor garantir
    def processar_pedido(self, conn):
        mensagem = json.loads(conn.recv(1024).decode())  # Talvez fosse bom aumentar o tamanho, mas por enquanto vou deixar 1MB mesmo
        conn.close()

        if (mensagem["operacao"] == "pedido_de_acesso") or (mensagem["operacao"] == "liberar_acesso"):
            self.processar_mensagem(mensagem)

    def processar_mensagem(self, mensagem):
        # Se o mutex permitir o relogio logico vai ser incrementado.
        with self.mutex:
            self.relogio = max(self.relogio, mensagem["relogio"]) + 1
            
            if self.ok:
                # Envia uma mensagem para confirmar o 'ok'
                self.enviar(mensagem["id_server"], {
                    "operacao": "resposta",
                    "id_server": self.id_server
                })
            else:
                # Se não estiver disponível vai pra fila de espera
                self.fila.append(mensagem)

    def executar_liberacao_de_acesso(self, mensagem):
        with self.mutex:
            # Remove o pedido da fila e processa se necessário
            if mensagem["id_server"] in [solicitacao["server_id"] for solicitacao in self.fila]:
                self.fila = [requisicao for requisicao in self.fila if solicitacao["id_server"] != message["id_server"]]
            
            if self.fila:
                proximo = self.fila.pop(0)
                self.ok = True
                self.enviar(proximo["id_server"], {
                    "operacao": "resposta",
                    "id_server": self.id_server
                })

    def executar(self):
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_request, args=(conn,)).start()

