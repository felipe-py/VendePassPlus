import socket
import json
import time
from threading import Lock, Thread

class RicartAgrawala:
    def __init__(self, server_id, servidores_conectados, timeout=5):
        self.server_id = server_id
        self.clock = 0
        self.queue = []
        self.responses_received = 0
        self.servidores_conectados = servidores_conectados  # Lista de IDs dos servidores conectados ('A', 'B', 'C')
        self.active_servers = set(servidores_conectados)  # Servidores que responderam com sucesso
        self.requesting_critical_section = False
        self.lock = Lock()
        self.timeout = timeout  # Tempo de espera por respostas

        # Dicionário com os IDs dos servidores e seus endereços
        self.server_addresses = {
            'A': ('127.0.0.1', 65431),
            'B': ('127.0.0.1', 65432),
            'C': ('127.0.0.1', 65433)
        }

    def incrementar_relogio(self):
        with self.lock:
            self.clock += 1
        return self.clock

    def atualizar_relogio(self, received_clock):
        with self.lock:
            self.clock = max(self.clock, received_clock) + 1

    def request_critical_section(self):
        self.incrementar_relogio()
        self.requesting_critical_section = True
        self.responses_received = 0
        self.active_servers = set(self.servidores_conectados)  # Reinicia a lista de servidores ativos

        # Envia solicitação de acesso para todos os outros servidores
        request_message = {
            "operacao": "pedido_acesso",
            "server_id": self.server_id,
            "clock": self.clock
        }
        
        # Envia mensagens de forma assíncrona e aguarda cada resposta com timeout
        threads = []
        for server_id in self.servidores_conectados:
            thread = Thread(target=self.send_message, args=(server_id, request_message))
            thread.start()
            threads.append(thread)

        # Esperar que cada thread finalize (até o tempo limite)
        for thread in threads:
            thread.join(self.timeout)

        # Continuar apenas com os servidores que responderam
        print(f"{self.server_id} recebeu respostas de {len(self.active_servers)} servidores: {self.active_servers}")
        
        # Prosseguir apenas com os servidores ativos que responderam
        while self.responses_received < len(self.active_servers):
            time.sleep(0.1)

    def release_critical_section(self):
        self.requesting_critical_section = False
        release_message = {
            "operacao": "liberar_acesso",
            "server_id": self.server_id
        }
        self.broadcast(release_message)

    def handle_message(self, message):
        # Verifica se a mensagem é de um servidor conhecido
        if "server_id" not in message or message["server_id"] not in self.servidores_conectados:
            print("Mensagem ignorada - origem não reconhecida ou não autorizada.")
            return  # Ignora a mensagem

        # Processa somente se a origem for um servidor conhecido
        operacao = message["operacao"]
        sender_id = message["server_id"]
        sender_clock = message["clock"]

        self.atualizar_relogio(sender_clock)

        if operacao == "pedido_acesso":
            self.queue.append((sender_id, sender_clock))
            self.queue.sort(key=lambda x: (x[1], x[0]))  # Ordena pelo relógio e pelo ID
            if not self.requesting_critical_section or (self.clock, self.server_id) < (sender_clock, sender_id):
                self.send_ok(sender_id)
        
        elif operacao == "liberar_acesso":
            # Remove o servidor que liberou o acesso da fila
            self.queue = [req for req in self.queue if req[0] != sender_id]
            if self.queue:
                next_server_id, _ = self.queue[0]
                self.send_ok(next_server_id)

        elif operacao == "resposta_ok":
            # Conta cada OK recebido
            self.responses_received += 1

    def send_ok(self, destination_server_id):
        ok_message = {
            "operacao": "resposta_ok",
            "server_id": self.server_id,
            "clock": self.incrementar_relogio()
        }
        self.send_message(destination_server_id, ok_message)

    def broadcast(self, message):
        # Envia uma mensagem para todos os servidores conectados
        for server_id in self.servidores_conectados:
            self.send_message(server_id, message)

    def send_message(self, destination_id, message):
        # Busca o endereço correto pelo ID do servidor
        address = self.server_addresses.get(destination_id)
        if address is None:
            print(f"Endereço para o servidor {destination_id} não encontrado.")
            return

        host, port = address
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((host, port))
                request_body = json.dumps(message)
                request = (
                    f"POST /pedido_acesso HTTP/1.1\r\n"
                    f"Host: {host}:{port}\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(request_body)}\r\n"
                    f"\r\n"
                    f"{request_body}"
                )
                s.sendall(request.encode())
                # Marca o servidor como ativo caso a resposta seja recebida
                self.active_servers.add(destination_id)
                print(f"{self.server_id} recebeu OK de {destination_id}")
        except (socket.timeout, ConnectionRefusedError) as e:
            # Remove o servidor da lista de ativos se ele não responder
            if destination_id in self.active_servers:
                self.active_servers.remove(destination_id)
            print(f"{self.server_id} não conseguiu contato com {destination_id} - {e}")

