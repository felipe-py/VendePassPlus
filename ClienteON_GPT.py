import socket
import json
import time
from models.client.cliente_utils import conectar, login, logout, enviar_dados, espacos, mostrar_rotas, comprar_passagem, mostrar_passagens, cancelar_compra

# Definição dos servidores disponíveis
SERVIDORES = [
    ('127.0.0.210', 65432),  # ServerA
    ('127.0.0.201', 65433),  # ServerB
    ('127.0.0.202', 65434)   # ServerC
]

# Função para tentar conectar a qualquer servidor disponível
def conectar_disponivel():
    for host, port in SERVIDORES:
        try:
            conexao = conectar(host, port)
            print(f"Conectado ao servidor {host}:{port}")
            return conexao
        except:
            print(f"Não foi possível conectar ao servidor {host}:{port}. Tentando o próximo...")
    print("Nenhum servidor disponível.")
    return None

def main():
    while True:
        s1 = conectar_disponivel()  # Conectar ao primeiro servidor disponível
        if not s1:
            print("Falha ao conectar a todos os servidores. Tentando novamente em 5 segundos...")
            time.sleep(5)
            continue
        
        espacos()
        user = login(s1)  # Tentar login com o servidor conectado
        if user == "sair":
            logout(s1)
            break
        elif user:
            while True:
                operacao = menu(user)
                if operacao == '1':  # Mostrar rotas e comprar passagens
                    rotas_a_serem_compradas = []
                    passagens_por_servidor = {0: [], 1: [], 2: []}  # Cada lista para um servidor

                    # Tentar mostrar rotas
                    try:
                        mostrar_rotas(s1)
                    except:
                        print("Erro ao carregar as rotas.")

                    # Solicitar rotas para compra
                    mais_rotas = 's'
                    while mais_rotas.lower() in ('y', 's'):
                        rotaID = input("\nInsira o ID da rota desejada ou pressione '0' para cancelar a operação: ")
                        if rotaID == '0':
                            print("Operação cancelada.")
                            break
                        rotas_a_serem_compradas.append(rotaID)
                        mais_rotas = input("\nGostaria de comprar mais uma rota? [y/N]: ")

                    # Distribuir rotas conforme servidor responsável
                    for rota in rotas_a_serem_compradas:
                        rota_id = int(rota)
                        if rota_id > 60:
                            passagens_por_servidor[2].append(rota)
                        elif rota_id > 30:
                            passagens_por_servidor[1].append(rota)
                        else:
                            passagens_por_servidor[0].append(rota)

                    # Enviar pedidos de compra para os servidores correspondentes
                    for i, rotas in passagens_por_servidor.items():
                        if rotas:
                            mensagem = {'cliente_id': user, 'rotas_a_serem_compradas': rotas}
                            host, port = SERVIDORES[i]
                            try:
                                conexao = conectar(host, port)
                                comprar_passagem(user, conexao, mensagem)
                                logout(conexao)  # Desconectar após operação
                            except:
                                print(f"Erro ao comprar passagens no servidor {host}:{port}")

                elif operacao == '2':  # Cancelar passagem
                    print(f"Passagens Compradas por {user}:")
                    try:
                        mostrar_passagens(s1, user)
                    except:
                        print("Erro ao exibir passagens.")

                    passagem_a_ser_cancelada = input("\nQual passagem gostaria de cancelar? (0 para sair): ")
                    if passagem_a_ser_cancelada != '0':
                        for host, port in SERVIDORES:
                            try:
                                conexao = conectar(host, port)
                                cancelar_compra(conexao, passagem_a_ser_cancelada, user)
                                logout(conexao)
                            except:
                                print(f"Erro ao cancelar passagem no servidor {host}:{port}")

                elif operacao == '3':  # Logout e sair
                    logout(s1)
                    break
                else:
                    print("Operação inválida. Tente novamente.")
                    espacos()
        else:
            print("Credenciais incorretas. Tente novamente.")
            espacos()
        time.sleep(1)

if __name__ == "__main__":
    main()

