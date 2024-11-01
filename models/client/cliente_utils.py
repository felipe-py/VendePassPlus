import socket
import json


#Função para criar um socket e iniciar a conexão com o servidor usando o TCP/IP4.
def conectar(HOST, PORT):
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((HOST, PORT))
    return s1

#Função para fechar a conexão criada pelo socket.
def desconectar(s1):
    s1.close()

#Essa função recebe um conjunto de dados retornados por uma função do cliente (que já vem como dicionario) e junta em um dicionario
#com o opcode. Depois envia os dados, aguarda a resposta do servidor e, quando ela chegar, retorna a resposta.
def enviar_dados(s1, opcode, dados):
    mensagem = {
        "opcode": opcode,
        "dados": dados
    }
    s1.sendall(json.dumps(mensagem).encode())

    # Recebe a resposta do servidor, lidando com mensagens fracionadas
    partes = []
    while True:
        parte = s1.recv(1024).decode()
        partes.append(parte)
        if len(parte) < 1024:
            break

    # Junta todas as partes recebidas em uma única string
    resposta = ''.join(partes)
    return json.loads(resposta)
#Essa função só manda uma mensagem antes de desconectar.
def logout(s1):
    print("Adeus")
    desconectar(s1)

#Função para realizar o login, recebe os inputs do usuário, manda para o servidor e, em caso de login bem sucedido, 
#retorna o usuário logado.
def login(s1):
    print("\nDigite SAIR para sair.\n")
    id = input("Digite seu ID: ")
    if id == "SAIR":
        espacos()
        # logout(s1)
        return "sair"
    else:
        senha = input("Digite sua senha: ")
        credenciais ={
            'id':id,
            'senha':senha
        } 
        resposta = enviar_dados(s1, 1, credenciais)
        print("\n")
        espacos()
        if resposta == "Logado com sucesso":
            return id
        else:
            print("Falha na autenticação.")
            return None
    return None

#Essa função solicita uma lista de rotas com assentos disponíveis para o servidor, e depois mostra os resultados ao
#usuário
def mostrar_rotas(s1):
    resposta = enviar_dados(s1, 2, {})
    for rota in resposta:
        print(f"ID: {rota['ID']} | Trecho: {rota['trecho']}")

#Essa função realiza a compra de passagens, ela chama 'mostrar_rotas' para que o usuário possa ver as rotas disponíveis
#antes de realizar a compra, o tratamento de solicitações improprias se dá no servidor.
def comprar_passagem(user, s1, mensagem):
    resposta = enviar_dados(s1, 3, mensagem)

    while (resposta != 'Compra realizada' and resposta != 'Acabaram as vagas') :
        espacos()
        print("Os seguintes trechos não tem mais vagas disponíveis:\n")
        for elemento in resposta:
            # print(f"Trecho: {elemento['rota']}") # Em caso de retornar passagem
            print(f"Trecho: {elemento['trecho']}") # Em caso de retornar rota

        seguir = input("\nAinda deseja seguir com a compra?[y/N]\n: ")
        if seguir.lower() == 's' or seguir.lower() == 'y':
            for i in resposta:
                if i['ID'] in rotas_a_serem_compradas:
                    j = i['ID']
                    rotas_a_serem_compradas.remove(j)
            mensagem = {
                'cliente_id': user,
                'rotas_a_serem_compradas': rotas_a_serem_compradas
            }
            resposta = enviar_dados(s1, 3, mensagem)
        elif seguir.lower() == 'n':
            espacos()
            print("A compra não foi realizada.")
            break

    if resposta == 'Compra realizada':
        espacos()
        print("\nCompra realizada com sucesso.")
    elif resposta == 'Acabaram as vagas':
        espacos()
        print("\nAs vagas acabaram.")

def mostrar_passagens(s1, user):
    mensagem = {'cliente_id': user}
    passagens = enviar_dados(s1, 4, mensagem)

    for passagem in passagens:
        print(f"ID: {passagem['id_passagem']} | Rota: {passagem['rota']}")

#Função para cancelar compra, funciona de forma similar a compra, manda o usuário pois o processo de cancelamento opera em
#dois bancos de dado, e em um deles o objeto é encontrado a partir do usuário.
def cancelar_compra(s1, passagemID, user):
    # mostrar_passagens(s1, user)
    # passagemID = input("\nInsira o ID da passagem ou pressione '0' para cancelar a operação: ")
    mensagem = {'id_passagem': passagemID, 'userID': user}
    resposta = enviar_dados(s1, 5, mensagem)
    print(f"{resposta}\n")
    espacos()

#Print de um separador.
def espacos():
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

#Menu do programa, fica rodando contínuamente para que depois de um operação o usuário possa realizar outras sem ter que logar novamente.
def menu(user):
    while True:
        print(f"Bem vindo(a) {user}, o que gostaria de fazer?\n\n")
        print("1. Comprar uma passagem")
        print("2. Cancelar uma compra")
        print("3. Sair")

        operacao = input("\n: ")
        espacos()
        return operacao

        # if operacao == '1':
        #     comprar_passagem(s1, user)
        # elif operacao == '2':
        #     cancelar_compra(s1, user)
        # elif operacao == '3':
        #     logout(s1)
        #     break
        # else:
        #     print("\nPor favor, selecione uma opção válida.")
