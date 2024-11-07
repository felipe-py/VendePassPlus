import socket
import threading
import struct
import json
import os
import time
from pathlib import Path
import requests

SERVERS = {
    'A': 'http://127.0.0.1:65431',
    'B': 'http://127.0.0.2:65432',
    'C': 'http://127.0.0.3:65433'
}



# Inicialização do relógio lógico e variáveis de controle para Ricart-Agrawala
relogio_logico = 0
ok_count = 0
fila_pedidos = []
solicitando_acesso = False
# conexoes_servidores = {}  # Servidores conectados com (IP, porta)


# Função para incrementar o relógio lógico de Lamport
def incrementar_relogio():
    global relogio_logico
    with mutex:
        relogio_logico += 1
    return relogio_logico

# Função para atualizar o relógio lógico com base em um valor recebido
def atualizar_relogio(received_clock):
    global relogio_logico
    with mutex:
        relogio_logico = max(relogio_logico, received_clock) + 1

# Função para enviar uma resposta fracionada ao cliente
def enviar_resposta(conexao_servidor, resposta):
    resposta_json = json.dumps(resposta)
    for i in range(0, len(resposta_json), 1024):
        conexao_servidor.sendall(resposta_json[i:i + 1024].encode())

# Função para enviar pedidos de acesso e gerenciar OKs recebidos
# def pedir_acesso(id_servidor):
#     print(f"{id_servidor} esta pedindo acesso a zona critica")
#     global ok_count
#     ok_count = 0  # Reset contador de OKs
#     meu_relogio = incrementar_relogio()
#     mensagem = {
#         "operacao": "pedido_acesso",
#         "id_servidor": id_servidor,
#         "relogio": meu_relogio
#     }
#
#     # Envia o pedido a todos os servidores conectados
#     for (ip, porta), conexao in conexoes_servidores.items():
#         try:
#            conexao.sendall(json.dumps(mensagem).encode())
#         except Exception as e:
#             print(f"Erro ao enviar pedido para {ip}:{porta} - {e}")
#
#     # Aguardar o recebimento de todos os OKs
#     while ok_count < len(conexoes_servidores):
#         time.sleep(0.1)

def pedir_acesso(id_servidor):
    print(f"{id_servidor} está pedindo acesso à zona crítica")
    global ok_count
    ok_count = 0  # Reinicia o contador de OKs

    meu_relogio = incrementar_relogio()
    mensagem = {
        "operacao": "pedido_acesso",
        "id_servidor": id_servidor,
        "relogio": meu_relogio
    }

    # Envia pedidos de acesso para outros servidores
    for servidor, url in SERVERS.items():
        t = 0
        if servidor != id_servidor:  # Ignora o próprio servidor
            while t < 10:
                try:
                    response = requests.post(
                        f"{url}/ra_message",
                        json=mensagem,
                        timeout=2  # Timeout curto para conexões
                    )
                    if response.status_code == 200:
                        print(f"Pedido de acesso enviado para {servidor} com sucesso.")
                        break
                    else:
                        print(f"Erro ao enviar pedido para {servidor}: {response.status_code}")
                        break
                except requests.exceptions.RequestException as e:
                    # Incrementa o contador de OKs para servidores que não responderam (presume-se inativos)
                    t += 1
                    time.sleep(0.1)
            if t > 9:
                print(f"Servidor {servidor} parece estar offline. Ignorando para acesso à zona crítica.")
                ok_count += 1   
            # print(ok_count)
    # Aguarda OKs dos servidores ativos
    timeout = 30  
    start_time = time.time()
    while ok_count < len(SERVERS) - 1:  # Ignora servidores inativos
        if time.time() - start_time > timeout:
            raise TimeoutError("Timeout esperando respostas dos servidores ativos")
        time.sleep(0.1)
    
    print(f"{id_servidor} recebeu OKs suficientes para acessar a zona crítica.")


# Função para liberar acesso após sair da seção crítica
# def liberar_acesso(id_servidor):
#     mensagem = {
#         "operacao": "liberar_acesso",
#         "id_servidor": id_servidor
#     }
#     for (ip, porta), conexao in conexoes_servidores.items():
#         try:
#             conexao.sendall(json.dumps(mensagem).encode())
#         except Exception as e:
#             print(f"Erro ao enviar liberação para {ip}:{porta} - {e}")
#     print(f"{id_servidor} esta liberando o acesso a zona critica")

def liberar_acesso(id_servidor):
    mensagem = {
        "operacao": "liberar_acesso",
        "id_servidor": id_servidor,
        "relogio": 0 # Ta aqui só pra não ficar dando excessão toda hora, mas não usa pra nada.
    }

    # Envia mensagens de liberação
    for servidor, url in SERVERS.items():
        if servidor != id_servidor:
            try:
                response = requests.post(
                    f"{url}/ra_message",
                    json=mensagem,
                    timeout=5
                )
                if response.status_code != 200:
                    print(f"Erro ao enviar liberação para {servidor}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erro de conexão com servidor {servidor}: {e}")

    print(f"{id_servidor} esta liberando o acesso a zona critica")


# Função para processar mensagens de pedidos de acesso e liberação de acesso
# def processar_mensagem(mensagem, id_servidor):
#     global ok_count
#     operacao = mensagem["operacao"]
#
#     if operacao == "pedido_acesso":
#         # Atualiza o relógio lógico e ordena a fila de pedidos
#         atualizar_relogio(mensagem["relogio"])
#         fila_pedidos.append(mensagem)
#         fila_pedidos.sort(key=lambda x: (x["relogio"], x["id_servidor"]))
#
#         # Envia OK para o servidor se este tem prioridade
#         if (relogio_logico, id_servidor) < (mensagem["relogio"], mensagem["id_servidor"]):
#             enviar_ok(mensagem["id_servidor"])
#
#     elif operacao == "liberar_acesso":
#         # Remove o pedido da fila após liberação
#         fila_pedidos[:] = [req for req in fila_pedidos if req["id_servidor"] != mensagem["id_servidor"]]
#         if fila_pedidos:
#             # Envia OK ao próximo servidor na fila
#             proximo = fila_pedidos.pop(0)
#             enviar_ok(proximo["id_servidor"])
#
#     elif operacao == "resposta_ok":
#         # Conta cada OK recebido
#         ok_count += 1


def processar_mensagem(mensagem, id_servidor):
    global ok_count, solicitando_acesso, relogio_logico, fila_pedidos

    operacao = mensagem["operacao"]
    mensagem_relogio = mensagem["relogio"]
    mensagem_id_servidor = mensagem["id_servidor"]

    # Atualiza o relógio lógico ao receber uma mensagem
    atualizar_relogio(mensagem_relogio)

    if operacao == "pedido_acesso":
        print(f"Processando pedido de acesso de {mensagem_id_servidor} com relógio {mensagem_relogio}")
        
        # Adiciona o pedido à fila e ordena a fila de pedidos
        fila_pedidos.append(mensagem)
        fila_pedidos.sort(key=lambda x: (x["relogio"], x["id_servidor"]))

        # Envia OK se:
        # 1. O servidor não está solicitando acesso, ou
        # 2. O pedido na mensagem tem prioridade sobre o pedido do próprio servidor
        if not solicitando_acesso or (relogio_logico, id_servidor) > (mensagem_relogio, mensagem_id_servidor):
            enviar_ok(mensagem_id_servidor)
        else:
            print(f"Servidor {id_servidor} mantém a prioridade sobre {mensagem_id_servidor}")

    elif operacao == "liberar_acesso":
        print(f"Processando liberação de acesso de {mensagem_id_servidor}")
        
        # Remove o pedido da fila e processa o próximo
        fila_pedidos = [req for req in fila_pedidos if req["id_servidor"] != mensagem_id_servidor]
        if fila_pedidos:
            proximo = fila_pedidos[0]
            enviar_ok(proximo["id_servidor"])

    elif operacao == "resposta_ok":
        ok_count += 1
        print(f"Servidor {id_servidor} recebeu OK de {mensagem_id_servidor}. Total de OKs: {ok_count}")




# Função para enviar confirmação de OK ao servidor
# def enviar_ok(id_destino):
#     mensagem = {"operacao": "resposta_ok"}
#     conexao = conexoes_servidores.get(id_destino)
#     if conexao:
#         ip, porta = conexao
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((ip, porta))
#                 s.sendall(json.dumps(mensagem).encode())
#         except Exception as e:
#             print(f"Erro ao enviar OK para {id_destino}: {e}")



def enviar_ok(id_servidor_destino):
    # Envia uma resposta de OK para o servidor destino
    mensagem_ok = {
        "operacao": "resposta_ok",
        "id_servidor": id_servidor_destino,
        "relogio": relogio_logico
    }
    try:
        # Obtém a URL do servidor destino do dicionário SERVERS
        url_destino = SERVERS[id_servidor_destino]
        response = requests.post(f"{url_destino}/ra_message", json=mensagem_ok, timeout=5)
        
        # Verifica se o envio foi bem-sucedido
        if response.status_code == 200:
            print(f"OK enviado com sucesso para {id_servidor_destino}")
        else:
            print(f"Erro ao enviar OK para {id_servidor_destino}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar OK para {id_servidor_destino}: {e}")


# Criado o MUTEX que irá controlar as operações em zonas críticas (na prática as alterações no BD).
mutex = threading.Lock()

# Definição de diretórios para facilitar outras funções.
diretorio_do_servidor = Path(__file__).parent
diretorio_dos_BD   = diretorio_do_servidor.parent.parent / 'dados'

# Função para fracionar respostas muito grandes em pedaços menores.
def enviar_resposta(conexao_servidor, resposta):
    resposta_json = json.dumps(resposta)
    # Fracione a mensagem em pedaços de 1024 bytes
    for i in range(0, len(resposta_json), 1024):
        conexao_servidor.sendall(resposta_json[i:i + 1024].encode())

# Função para realizar a conexão entre servidores, diferente da conexão entre cliente e servidor, essa tenta a reconexão
def conectar_com_servidor(HOST, PORT, tempo):
    while True:
        print(f"tentando conectar a {HOST} na porta {PORT}")
        try:
            s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s1.connect((HOST, PORT))
            print(f"conectado a {HOST} na porta {PORT}")
            time.sleep(tempo)
            return
        except:
            print(f"Erro ao conectar ao servidor")
            time.sleep(tempo)

# Função para carregar dados de forma genérica
def carregar_dados(arquivo):
    try:
        with open(arquivo, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {arquivo}")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    return None

# Função para salvar dados de forma genérica
def salvar_dados(arquivo, BD):
    try:
        with open(arquivo, 'w') as arquivo:
            json.dump(BD, arquivo, indent=4)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

# Funções específicas para carregar as rotas, passagens e usuarios. Elas rotornam seus respectivos Bancos de Dados(BD)
def carregar_rotas(servidor):
    diretorio_das_rotas = os.path.join(diretorio_dos_BD, f'server{servidor}/rotas_server_{servidor}.json')
    print(f"Arquivo de rotas: {diretorio_das_rotas}\n")
    return carregar_dados(diretorio_das_rotas)
    
def carregar_passagens(servidor):
    diretorio_das_passagens = os.path.join(diretorio_dos_BD, f'server{servidor}/passagens_server_{servidor}.json')
    print(f"Arquivo das passagens: {diretorio_das_passagens}\n")
    return carregar_dados(diretorio_das_passagens)

def carregar_usuarios():
    diretorio_dos_usuarios = os.path.join(diretorio_dos_BD, 'clientes.json')
    print(f"Arquivo de usuarios: {diretorio_dos_usuarios}\n")
    return carregar_dados(diretorio_dos_usuarios)

# Funções para atualizar os bancos de dados. Elas recebem um BD que foi editado(como 'rotas') e chama a função
# 'salvar_dados' para realizar o dump no arquivo correto.
def atualizar_rotas(rotas):
    diretorio_das_rotas = os.path.join(diretorio_dos_BD, 'rotas.json')
    salvar_dados(diretorio_das_rotas, rotas)


def atualizar_passagens(passagens):
    diretorio_das_passagens = os.path.join(diretorio_dos_BD, 'passagens.json')
    salvar_dados(diretorio_das_passagens, passagens)

def atualizar_usuarios(usuarios):
    diretorio_dos_usuarios = os.path.join(diretorio_dos_BD, 'clientes.json')
    salvar_dados(diretorio_dos_usuarios, usuarios)

# Função para realizar o login, ela recebe o ID e a senha e compara a um usuário do BD 'clientes' e retorna uma mensagem
# que vai ser interpretada no cliente como uma autorização (ou não) para prosseguir com o menu
# models/service/server_utils.py

def logar(id, senha, usuarios):
    if usuarios is None or len(usuarios) == 0:
        return {"status": "falha", "mensagem": "A lista de usuarios está vazia"}
    
    for user in usuarios:
        if user['id'] == id and user['senha'] == senha:
            return {"status": "sucesso", "mensagem": "Logado com sucesso"}
    
    return {"status": "falha", "mensagem": "Login falhou"}

# Função para contar o numero de passagens já criadas, importante para determinar o ID de uma nova passagem a ser gerada
def contar_passagens(usuarios):
    contador = 1
    for user in usuarios:
        for passagem in user['passagens']:
            contador +=1
    print(contador)
    return contador
