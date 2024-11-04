import socket
import threading
import struct
import json
import os
import time
from pathlib import Path
# import schedule



# Inicialização do relógio lógico e variáveis de controle para Ricart-Agrawala
relogio_logico = 0
ok_count = 0
fila_pedidos = []
conexoes_servidores = {}  # Servidores conectados com (IP, porta)

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
def pedir_acesso(id_servidor):
    global ok_count
    ok_count = 0  # Reset contador de OKs
    meu_relogio = incrementar_relogio()
    mensagem = {
        "operacao": "pedido_acesso",
        "id_servidor": id_servidor,
        "relogio": meu_relogio
    }

    # Envia o pedido a todos os servidores conectados
    for (ip, porta), conexao in conexoes_servidores.items():
        try:
            conexao.sendall(json.dumps(mensagem).encode())
        except Exception as e:
            print(f"Erro ao enviar pedido para {ip}:{porta} - {e}")

    # Aguardar o recebimento de todos os OKs
    while ok_count < len(conexoes_servidores):
        time.sleep(0.1)

# Função para liberar acesso após sair da seção crítica
def liberar_acesso(id_servidor):
    mensagem = {
        "operacao": "liberar_acesso",
        "id_servidor": id_servidor
    }
    for (ip, porta), conexao in conexoes_servidores.items():
        try:
            conexao.sendall(json.dumps(mensagem).encode())
        except Exception as e:
            print(f"Erro ao enviar liberação para {ip}:{porta} - {e}")

# Função para processar mensagens de pedidos de acesso e liberação de acesso
def processar_mensagem(mensagem, id_servidor):
    global ok_count
    operacao = mensagem["operacao"]

    if operacao == "pedido_acesso":
        # Atualiza o relógio lógico e ordena a fila de pedidos
        atualizar_relogio(mensagem["relogio"])
        fila_pedidos.append(mensagem)
        fila_pedidos.sort(key=lambda x: (x["relogio"], x["id_servidor"]))

        # Envia OK para o servidor se este tem prioridade
        if (relogio_logico, id_servidor) < (mensagem["relogio"], mensagem["id_servidor"]):
            enviar_ok(mensagem["id_servidor"])

    elif operacao == "liberar_acesso":
        # Remove o pedido da fila após liberação
        fila_pedidos[:] = [req for req in fila_pedidos if req["id_servidor"] != mensagem["id_servidor"]]
        if fila_pedidos:
            # Envia OK ao próximo servidor na fila
            proximo = fila_pedidos.pop(0)
            enviar_ok(proximo["id_servidor"])

    elif operacao == "resposta_ok":
        # Conta cada OK recebido
        ok_count += 1

# Função para enviar confirmação de OK ao servidor
def enviar_ok(id_destino):
    mensagem = {"operacao": "resposta_ok"}
    conexao = conexoes_servidores.get(id_destino)
    if conexao:
        ip, porta = conexao
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, porta))
                s.sendall(json.dumps(mensagem).encode())
        except Exception as e:
            print(f"Erro ao enviar OK para {id_destino}: {e}")
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
def logar(id, senha, usuarios):
    if usuarios is None:
        print("A lista de usuarios esta vazia")
    for user in usuarios:
        if user['id'] == id and user['senha'] == senha:
            return "Logado com sucesso"
    return "Login falhou"

# Função para contar o numero de passagens já criadas, importante para determinar o ID de uma nova passagem a ser gerada
def contar_passagens(usuarios):
    contador = 1
    for user in usuarios:
        for passagem in user['passagens']:
            contador +=1
    print(contador)
    return contador


# Essa função executa a compra de uma passagem, detalhe que o processo de compra envolve mais do que só essa função, as etapas
# desse processo são determinadas no cliente.
def comprar_passagem(userID, rotas_a_serem_compradas , rotas, passagens, usuarios, servidor):
    # Primeiro são criados os vetores que irão guardar as rotas sem vagas e as passagens criadas,
    # porém ainda não escritas no BD
    rotas_sem_vagas = []
    passagens_para_registrar = []
    
    # Dois loops aninhados para encontrar a rota buscada, depois de encontrada será verificada
    # se ainda há assentos disponiveis (ja com o MUTEX) e então será feita a passagem
    for rota_compra in rotas_a_serem_compradas:
        for rota_no_BD in rotas:
            if rota_compra == rota_no_BD['ID']:
                print(f"Rota com ID:{rota_compra} encontrada.")
                with mutex:
                    if rota_no_BD['assentos_disponiveis'] > 0:
                        print(f"Há assentos disponíveis na rota {rota_compra}.")
                        # Atualiza o contador a cada nova passagem para usar no ID
                        cont = contar_passagens(usuarios)
                        contar_novamente = cont + len(passagens_para_registrar)  
                        print(f"As informações para a compra são: ID:{contar_novamente}, usuario:{userID}, rota:{rota_no_BD['trecho']}")
                        # Apesar da passagem ser criada aqui ela ainda não foi salva em arquivo, 
                        # ela está sendo guardada no vetor "passagens_para_registrar"
                        nova_passagem = {
                            "id_passagem": contar_novamente, 
                            "cliente_id": userID,
                            "rota": rota_no_BD['trecho'],
                            "estaCancelado": False,
                            "servidor": servidor
                        }
                        print(f"Foi criada a passagem {nova_passagem['id_passagem']}.")
                        passagens_para_registrar.append(nova_passagem)
                        # Aqui a rota já é alterada no BD, o motivo do BD de rotas ser atualizado
                        # e o BD das passagens não é que o BD de rotas é 'investigado' em busca
                        # de assentos diponíveis, então ele precisa ser atualizado a cada operação
                        # contudo para as passagens isso apenas adicionaria um procedimento que
                        # talvez precisasse ser desfeito a depender se as outras rotas teriam vagas
                        # ou não desperdiçando processamento.
                        rota_no_BD['assentos_disponiveis'] -= 1
                        atualizar_rotas(rotas)
                    else:
                        # Caso não haja vagas a rota vai ser guardada para um return
                        rotas_sem_vagas.append(rota_no_BD)
    # Caso todas as rotas tenham vagas as passagens guardadas no vetor são escritas nos BD de passagens
    # e usuarios
    if len(rotas_sem_vagas) == 0:
        # Operações que envolvem a escrita de dados precisam ser controladas pelo MUTEX para evitar
        # condições de corrida
        with mutex:
            for p in passagens_para_registrar:
                passagens.append(p)
                for u in usuarios:
                    if p['cliente_id'] == u['id']:
                        historico = u['passagens']
                        historico.append(p)
            atualizar_passagens(passagens)
            atualizar_usuarios(usuarios) 
        return 'Compra realizada'
    # Caso todas as rotas estejam sem vagas, não há sentido em 'continuar' qualquer operação, então
    # so há o retorno
    elif len(rotas_sem_vagas) == len(rotas_a_serem_compradas):
        return 'Acabaram as vagas'
    # Só entra nesse else se houveram um conjunto de rotas sem vagas menor do que o número de pedidos
    # da compra, nesse caso o BD das rotas é atualizado para retornar as vagas (já que a compra não foi
    # feita) sem vagas, detalhe que o usuário pode escolher comprar as outras rotas, mas nesse caso o
    # cliente realimentaria essa função com o conjunto de rotas "original" sem as rotas que foram removidas
    # pela ausencia de vagas
    else:
        with mutex:
            for p in passagens_para_registrar:
                for r in rotas:
                    if p['rota'] == r['trecho']:
                        r['assentos_disponiveis'] += 1
            atualizar_rotas(rotas)
        return rotas_sem_vagas                   

# Função que busca as passagens de um dado usuário e retorna todas que não estejam marcadas como canceladas.
def buscar_passagens_de_usuario(userID, usuarios):
    passagens_validas = []
    for user in usuarios:
        if (user['id'] == userID):
            print("usuario encontrado")
            for passagem in user['passagens']:
                if passagem['estaCancelado'] == 0:
                    passagens_validas.append(passagem)
            print(f"{passagens_validas}")
            return passagens_validas
    return None

# Função que cancela uma passagem, para todos os propósitos a requerida passagem não existe mais, contudo
# o registro dela permanece no BD das passagens e nas passagens do usuário no BD dos clientes, porém marcado
# como passagem cancelada.
def cancelar_passagem(passagemID, userID, passagens, usuarios, servidor):
    print(f"\npassagemID: {passagemID} | userID: {userID} | passagens: {passagens} | usuarios: {usuarios} | servidor: {servidor}\n")
    if int(passagemID) == 0:
        print("cancelamento cancelado")
        return "Voltando para o menu"
    for user in usuarios:
        for passagem in user['passagens']:
            if passagem['id_passagem'] == int(passagemID):
                print("A passagem foi encontrada.")
                if passagem['cliente_id'] != userID:
                    print("Passagem de outro usuario")
                    return f"Essa passagem pertence ao usuario {passagem['cliente_id']}."
                if passagem['servidor'] != servidor:
                    print("Essa passagem pertence a outro servidor")
                    return
                if passagem['estaCancelado'] != 1:
                    print(f"o cliente na passagem eh: {passagem['cliente_id']}\no userID eh: {userID}")
                    passagem['estaCancelado'] = 1
                    for user in usuarios:
                        if user['id'] == userID:
                            for p in user['passagens']:
                                if int(p['id_passagem']) == int(passagemID):
                                    p['estaCancelado'] = 1
                    with mutex:
                        atualizar_passagens(passagens)
                        atualizar_usuarios(usuarios)
                    return "Passagem cancelada com sucesso."
                else:
                    return "A passagem ja foi cancelada"
    return "Passagem não encontrada."

# Função para mostrar as rotas disponíveis para compra a partir da solicitação do cliente
def mostrar_rotas(rotas):
    rotas_disponiveis = []
    for rota in rotas:
        if rota['assentos_disponiveis']>0:
            rotas_disponiveis.append(rota)
    print(f"tem um total de {len(rotas_disponiveis)} rotas disponiveis")
    for r in rotas_disponiveis:
        print(f"{r['trecho']}")
    return rotas_disponiveis

def verificar_quantidade(rotas, rotaID):
    for rota in rotas:
        if rotaID == rota['ID']:
            return rota['assentos_disponiveis']
    return 0

# Essa função interpreta a solicitação feita para o servidor, ela separa o 'opcode' da mensagem, seleciona
# a função a ser executada e envia os argumentos para sua execução.
def tratar_cliente(conexao_servidor, usuarios, passagens, rotas, id_servidor):
    try:
        while True:
            mensagem = conexao_servidor.recv(1024).decode()
            if not mensagem:
                break
            dados = json.loads(mensagem)
            opcode = dados['opcode']
            conteudo = dados['dados']

            # Atualiza o arquivo que pode ser alterado por outros servidores.
            usuarios = carregar_usuarios()

            # Pede acesso à seção crítica para operações no BD
            pedir_acesso(id_servidor)

            # Processa a solicitação baseada no opcode
            print(f"Processando a operação {opcode} com dados: {conteudo}")
            if opcode == 1:
                resultado = logar(conteudo['id'], conteudo['senha'], usuarios)
            elif opcode == 2:
                resultado = mostrar_rotas(rotas)
            elif opcode == 3:
                resultado = comprar_passagem(conteudo['cliente_id'], conteudo['rotas_a_serem_compradas'], rotas, passagens, usuarios, id_servidor)
            elif opcode == 4:
                resultado = buscar_passagens_de_usuario(conteudo['cliente_id'], usuarios)
            elif opcode == 5:
                resultado = cancelar_passagem(conteudo['id_passagem'], conteudo['userID'], passagens, usuarios, id_servidor)
            elif opcode == 6:
                resultado = verificar_quantidade(rotas, conteudo['rotaID'])
            else:
                resultado = "Operação inválida"
            enviar_resposta(conexao_servidor, resultado)

            # Libera o acesso após a operação na seção crítica
            liberar_acesso(id_servidor)

    except Exception as e:
        print(f"Erro ao tratar cliente: {e}")
    finally:
        print("Conexão encerrada.")
        conexao_servidor.close()
