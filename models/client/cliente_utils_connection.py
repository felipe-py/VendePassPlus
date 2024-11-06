import requests

# LISTA DOS SERVIDORES DISPONÍVEIS NO SISTEMA, COM SEUS RESPECTIVOS IP E PORTA
SERVIDORES = {
    'A': 'http://127.0.0.1:65431',
    'B': 'http://127.0.0.2:65432',
    'C': 'http://127.0.0.3:65433'
}

# grupo de funções para envio dos dados necessários nas mais diversas operações no servidor
# é feito o envio das informações necessárias em cada função

def verificar_servidor(servidor):
    try:
        response = requests.get(f"{SERVIDORES[servidor]}/status")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Servidor {servidor} não está ativo: {e}")
        return None

def realizar_login(servidor, usuario_id, senha):
    try:
        data = {'id': usuario_id, 'senha': senha}
        response = requests.post(f"{SERVIDORES[servidor]}/login", json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao realizar login no servidor {servidor}: {e}")
        return None

def listar_rotas(servidor):
    try:
        response = requests.get(f"{SERVIDORES[servidor]}/rotas")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao listar rotas no servidor {servidor}: verifique se o servidor esta online.")
        return None

def listar_passagens(servidor):
    try:
        response = requests.get(f"{SERVIDORES[servidor]}/usuarios")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro na lista de usuários {servidor}: {e}")
        return None

def comprar_passagem(servidor, cliente_id,rotas_carrinho):
    try:
        data = {'servidor': servidor, 'cliente_id': cliente_id, 'rotas_a_serem_compradas': rotas_carrinho}
        response = requests.post(f"{SERVIDORES[servidor]}/comprar_passagem", json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao comprar passagem no servidor {servidor}: {e}")
        return None

def cancelar_passagem(servidor, passagem_id, cliente_id):
    try:
        data = {'servidor': servidor, 'cliente_id': cliente_id, 'passagem_id': passagem_id}
        response = requests.delete(f"{SERVIDORES[servidor]}/cancelar_passagem", json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao cancelar passagem no servidor {servidor}: {e}")
        return None
    
