from flask import Flask, request, jsonify
from models.service.server_utils import *
import threading

app = Flask(__name__)

def atualizar():
    rotas = carregar_rotas("2")
    usuarios = carregar_usuarios()
    passagens = carregar_passagens("2")

# Carregar dados ao iniciar o servidor
rotas = carregar_rotas("2")  # Presumindo que ServerB usa um arquivo de rotas específico
usuarios = carregar_usuarios()
passagens = carregar_passagens("2")  # Presumindo que ServerB usa um arquivo de passagens específico

SERVER_ID = 'B'
SERVERS = {
    'A': 'http://127.0.0.1:65431',
    'C': 'http://127.0.0.1:65433'
}

# Mutex para operações locais
mutex = threading.Lock()

@app.route('/ra_message', methods=['POST'])
def pegar_mensagem():
    print("mensagem recebida.")
    mensagem = request.get_json()
    print(mensagem)
    processar_mensagem(mensagem, 'B')  # 'B' é o ID deste servidor
    return jsonify({'status': 'mensagem processada'})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'ativo'})

@app.route('/login', methods=['POST'])
def realizar_login():
    # pedir_acesso('B')
    dados = request.get_json()
    usuario_id = dados['id']
    senha = dados['senha']
    
    # Chamar a função de login
    resultado_login = logar(usuario_id, senha, usuarios)
    # liberar_acesso('B')
    return jsonify(resultado_login)

@app.route('/rotas', methods=['GET'])
def listar_rotas():
    atualizar()
    return jsonify(rotas)

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    atualizar()
    return jsonify(usuarios)

@app.route('/passagens', methods=['GET'])
def listar_passagens():
    atualizar()
    return jsonify(passagens)

@app.route('/comprar_passagem', methods=['POST'])
def comprar_passagem():
    atualizar()
    dados = request.get_json()
    servidor = dados['servidor']
    userID = dados['cliente_id']
    rotas_a_serem_compradas = dados['rotas_a_serem_compradas']

    rotas_sem_vagas = []
    passagens_para_registrar = []

    for rota_compra in rotas_a_serem_compradas:
        rota_encontrada = False
        for rota_no_BD in rotas:
            if int(rota_compra) == int(rota_no_BD['ID']):
                rota_encontrada = True
                print(f"Rota com ID:{rota_compra} encontrada.")
                pedir_acesso('B')
                with mutex:
                    if rota_no_BD['assentos_disponiveis'] > 0:
                        print(f"Há assentos disponíveis na rota {rota_compra}.")
                        cont = contar_passagens(usuarios)
                        contar_novamente = cont + len(passagens_para_registrar)  
                        nova_passagem = {
                            "id_passagem": contar_novamente, 
                            "cliente_id": userID,
                            "rota": rota_no_BD['trecho'],
                            "estaCancelado": False,
                            "servidor": servidor
                        }
                        print(f"Foi criada a passagem {nova_passagem['id_passagem']}.")
                        passagens_para_registrar.append(nova_passagem)
                        for rota in rotas:
                            if rota['ID'] == rota_no_BD['ID']:
                                rota['assentos_disponiveis'] -= 1
                        atualizar_rotas(rotas)
                    else:
                        rotas_sem_vagas.append(rota_no_BD)
                liberar_acesso('B')
                break
        if not rota_encontrada:
            print(f"Rota com ID:{rota_compra} não encontrada.")

    if len(rotas_sem_vagas) == 0:
        pedir_acesso('B')
        with mutex:
            for p in passagens_para_registrar:
                passagens.append(p)
                for u in usuarios:
                    if p['cliente_id'] == u['id']:
                        historico = u['passagens']
                        historico.append(p)
            atualizar_passagens(passagens)
            atualizar_usuarios(usuarios)
        liberar_acesso('B')
        return jsonify({'status': 'compra realizada com sucesso'}), 200
    elif len(rotas_sem_vagas) == len(rotas_a_serem_compradas):
        return jsonify({'status': 'acabaram as vagas'}), 409
    else:
        pedir_acesso('B')
        with mutex:
            for p in passagens_para_registrar:
                for r in rotas:
                    if p['rota'] == r['trecho']:
                        r['assentos_disponiveis'] += 1
            atualizar_rotas(rotas)
        liberar_acesso('B')
        return jsonify({'status': 'rotas indisponíveis', 'rotas_sem_vagas': rotas_sem_vagas}), 206


@app.route('/cancelar_passagem', methods=['DELETE'])
def cancelar_passagem():
    atualizar()
    dados = request.get_json()
    servidor = dados['servidor']
    userID = dados['cliente_id']
    passagemID = dados['passagem_id']

    print(f"\npassagemID: {passagemID} | userID: {userID} | passagens: {passagens} | usuarios: {usuarios} | servidor: {servidor}\n")
    if int(passagemID) == 0:
        print("cancelamento cancelado")
        return jsonify("Voltando para o menu")
    for user in usuarios:
        for passagem in user['passagens']:
            if passagem['id_passagem'] == int(passagemID):
                print("A passagem foi encontrada.")
                if passagem['cliente_id'] != userID:
                    print("Passagem de outro usuario")
                    return jsonify(f"Essa passagem pertence ao usuario {passagem['cliente_id']}.")
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
                    pedir_acesso('B')
                    with mutex:
                        atualizar_passagens(passagens)
                        atualizar_usuarios(usuarios)
                    liberar_acesso('B')
                    # Liberar a seção crítica após cancelamento
                    # ricart_agrawala.release_critical_section()
                    return jsonify("Passagem cancelada com sucesso.")
                else:
                    # ricart_agrawala.release_critical_section()
                    return jsonify("A passagem ja foi cancelada")

    return jsonify("Passagem não encontrada.")

if __name__ == '__main__':
    app.run(host='127.0.0.2', port=65432)

