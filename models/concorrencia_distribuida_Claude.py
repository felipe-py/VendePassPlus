import socket
import json
import threading
import time
from typing import List, Dict, Tuple, Optional
from queue import PriorityQueue

class RicartAgrawalaServer:
    def __init__(self, server_id: int, servers: List[Tuple[str, int]]):
        self.server_id = server_id
        self.servers = servers
        self.logical_clock = 0
        self.request_timestamp = 0
        self.state = 'RELEASED'  # RELEASED, WANTED, HELD
        self.deferred_replies: List[Dict] = []
        self.replies_received = 0
        self.mutex = threading.Lock()
        self.server_connections: Dict[int, Optional[socket.socket]] = {}
        self.is_running = True
        
    def increment_clock(self) -> int:
        with self.mutex:
            self.logical_clock += 1
            return self.logical_clock
    
    def update_clock(self, received_timestamp: int) -> int:
        with self.mutex:
            self.logical_clock = max(self.logical_clock, received_timestamp) + 1
            return self.logical_clock
            
    def connect_to_servers(self):
        """Tenta conectar-se a outros servidores periodicamente"""
        while self.is_running:
            for i, (host, port) in enumerate(self.servers):
                if i != self.server_id and i not in self.server_connections:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((host, port))
                        self.server_connections[i] = sock
                        print(f"Conectado ao servidor {i}")
                        # Inicia thread para receber mensagens deste servidor
                        threading.Thread(target=self.handle_server_messages, 
                                      args=(sock, i)).start()
                    except:
                        print(f"Não foi possível conectar ao servidor {i}")
            time.sleep(3)  # Tenta reconectar a cada 3 segundos

    def handle_server_messages(self, sock: socket.socket, server_id: int):
        """Manipula mensagens recebidas de outros servidores"""
        try:
            while self.is_running:
                data = sock.recv(1024).decode()
                if not data:
                    break
                    
                message = json.loads(data)
                self.process_message(message, server_id)
                
        except Exception as e:
            print(f"Erro ao receber mensagem do servidor {server_id}: {e}")
        finally:
            sock.close()
            del self.server_connections[server_id]

    def process_message(self, message: Dict, sender_id: int):
        """Processa mensagens recebidas seguindo o algoritmo Ricart-Agrawala"""
        with self.mutex:
            msg_type = message['type']
            if msg_type == 'REQUEST':
                received_timestamp = message['timestamp']
                self.update_clock(received_timestamp)
                
                # Decide se envia REPLY imediatamente ou adia
                if (self.state == 'HELD' or 
                    (self.state == 'WANTED' and 
                     (self.request_timestamp < received_timestamp or
                      (self.request_timestamp == received_timestamp and 
                       self.server_id < sender_id)))):
                    self.deferred_replies.append({
                        'server_id': sender_id,
                        'timestamp': received_timestamp
                    })
                else:
                    self.send_reply(sender_id)
                    
            elif msg_type == 'REPLY':
                self.replies_received += 1
                if (self.state == 'WANTED' and 
                    self.replies_received == len(self.servers) - 1):
                    self.state = 'HELD'
                    
    def request_critical_section(self):
        """Solicita acesso à seção crítica"""
        with self.mutex:
            self.state = 'WANTED'
            self.request_timestamp = self.increment_clock()
            self.replies_received = 0
            
        # Envia REQUEST para todos os outros servidores
        message = {
            'type': 'REQUEST',
            'timestamp': self.request_timestamp,
            'server_id': self.server_id
        }
        
        for server_id, sock in self.server_connections.items():
            if sock:
                try:
                    sock.sendall(json.dumps(message).encode())
                except:
                    print(f"Erro ao enviar REQUEST para servidor {server_id}")
                    
        # Aguarda receber todas as respostas
        while self.replies_received < len(self.server_connections):
            time.sleep(0.1)
            
    def release_critical_section(self):
        """Libera a seção crítica"""
        with self.mutex:
            self.state = 'RELEASED'
            
            # Envia REPLY para todas as requisições adiadas
            for deferred in self.deferred_replies:
                self.send_reply(deferred['server_id'])
            self.deferred_replies.clear()
            
    def send_reply(self, server_id: int):
        """Envia mensagem REPLY para um servidor"""
        if server_id in self.server_connections:
            message = {
                'type': 'REPLY',
                'timestamp': self.increment_clock(),
                'server_id': self.server_id
            }
            try:
                self.server_connections[server_id].sendall(
                    json.dumps(message).encode())
            except:
                print(f"Erro ao enviar REPLY para servidor {server_id}")
                
    def start(self):
        """Inicia o servidor"""
        # Inicia thread para conectar com outros servidores
        threading.Thread(target=self.connect_to_servers).start()
        
    def stop(self):
        """Para o servidor"""
        self.is_running = False
        for sock in self.server_connections.values():
            if sock:
                sock.close()
