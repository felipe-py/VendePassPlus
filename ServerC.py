from models.service.server_utils import *

# Criado o MUTEX que irá controlar as operações em zonas críticas (na prática as alterações no BD).
# mutex = threading.Lock()


# Essa função mantém o servidor ativo e conectado no endereço, ela também cria novas threads para conexões (até 8)
# e carrega os BD que serão usados nas funções.
def main():
    IP_SERVIDOR = '127.0.0.202'
    PORTA_SERVIDOR = 65434

    IP_SERVIDOR_A = '127.0.0.200'
    PORTA_SERVIDOR_A = 65432

    IP_SERVIDOR_B = '127.0.0.201'
    PORTA_SERVIDOR_B = 65433

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((IP_SERVIDOR, PORTA_SERVIDOR))
    servidor.listen(8)
    print(f"criado o socket\nIP: {IP_SERVIDOR}\nPorta: {PORTA_SERVIDOR}")

    rotas = carregar_rotas("3")
    print("carregado o BD de rotas")
    usuarios = carregar_usuarios()
    print("carregado o BD de usuarios")
    passagens = carregar_passagens("3")
    print("carregado o BD de passagens")

    print(f"Servidor conectado em {IP_SERVIDOR} na porta {PORTA_SERVIDOR}...")

    thread_B = threading.Thread(target=conectar_com_servidor, args=(IP_SERVIDOR_B, PORTA_SERVIDOR_B, 5))
    thread_A = threading.Thread(target=conectar_com_servidor, args=(IP_SERVIDOR_A, PORTA_SERVIDOR_A, 5))
    thread_B.start()
    thread_A.start()

    while True:
        conexao_servidor, endereco_cliente = servidor.accept()
        print(f"Nova conexão de {endereco_cliente}")
        cliente_thread = threading.Thread(target=tratar_cliente, args=(conexao_servidor, usuarios, passagens, rotas))
        cliente_thread.start()

main()



