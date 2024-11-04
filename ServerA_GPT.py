# ServerA.py
import socket
import threading
import time
from models.service.server_utils import *
from models.client.cliente_utils import conectar
from models.concorrencia_distribuida_GPT import Server

# Configurações de rede
IP_SERVIDOR = '127.0.0.210'
PORTA_SERVIDOR = 65432
SERVERS = [
    ("127.0.0.200", 65432),  # ServerA
    ("127.0.0.201", 65433),  # ServerB
    ("127.0.0.202", 65434)   # ServerC
]

# Inicialização do servidor Ricart-Agrawala
id_server = 0  # Identificador de ServerA
servidor_RA = Server(id_server, SERVERS)

# Função para tratar clientes e servidores
def tratar_conexao(conexao, usuarios, passagens, rotas):
    try:
        while True:
            servidor_RA.conectar_nos_outros_servidores()
            mensagem = conexao.recv(1024).decode()
            if not mensagem:
                break
            dados = json.loads(mensagem)
            opcode = dados['opcode']
            conteudo = dados['dados']
            
            # Sincronização de acesso ao arquivo 'clientes.json'
            servidor_RA.pedir_acesso()  # Envia pedido para acessar a seção crítica

            if opcode == 1:
                resultado = logar(conteudo['id'], conteudo['senha'], usuarios)
            elif opcode == 2:
                resultado = mostrar_rotas(rotas)
            elif opcode == 3:
                resultado = comprar_passagem(conteudo['cliente_id'], conteudo['rotas_a_serem_compradas'], rotas, passagens, usuarios)
            elif opcode == 4:
                resultado = buscar_passagens_de_usuario(conteudo['cliente_id'], usuarios)
            elif opcode == 5:
                resultado = cancelar_passagem(conteudo['id_passagem'], conteudo['userID'], passagens, usuarios)
            else:
                resultado = "Operação inválida"

            enviar_resposta(conexao, resultado)
            servidor_RA.liberar_acesso()  # Libera acesso à seção crítica após o processamento
    except Exception as e:
        print(f"Erro ao tratar conexão: {e}")
    finally:
        conexao.close()

# Função para aceitar conexões
def aceitar_conexoes(servidor, usuarios, passagens, rotas):
    while True:
        conexao, endereco = servidor.accept()
        print(f"Nova conexão de {endereco}")
        cliente_thread = threading.Thread(target=tratar_conexao, args=(conexao, usuarios, passagens, rotas))
        cliente_thread.start()

# Função principal
def main():
    # Configuração do servidor principal
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((IP_SERVIDOR, PORTA_SERVIDOR))
    servidor.listen(5)
    print(f"Servidor A escutando em {IP_SERVIDOR}:{PORTA_SERVIDOR}")

    # Carregar dados necessários
    rotas = carregar_rotas("1")
    usuarios = carregar_usuarios()
    passagens = carregar_passagens("1")

    # Iniciar threads de coordenação e aceitação de conexões
    threading.Thread(target=servidor_RA.executar).start()
    threading.Thread(target=aceitar_conexoes, args=(servidor, usuarios, passagens, rotas)).start()

if __name__ == "__main__":
    main()

