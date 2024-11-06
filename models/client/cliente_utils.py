from models.client.cliente_utils_connection import listar_rotas, comprar_passagem, cancelar_passagem, listar_passagens

# GRUPO DE FUNÇÕES RESPONSÁVEIS POR EVITAR ERROS NO INPUT DO USUÁRIO NO MENU
def verifica_escolha_servidor(servidor_escolhido):
    servidores = ['A','B','C']
    if servidor_escolhido not in servidores:
        return True
    return False

def verificar_escolha_menu(opcao):
    opcoes = ['1','2','3']
    if opcao not in opcoes:
        return True
    return False

def verificar_escolha_companhia_compra(escolha):
    escolhas = ['1','2']
    if escolha not in escolhas:
        return True
    return False

def retornar_rotas_disponiveis(rotas):
    return rotas

def filtrar_rotas(dicionario):
    rotas_livres = []
    for rota in dicionario:
        if rota['assentos_disponiveis'] != 0:
            rotas_livres.append(rota["ID"])
    
    return rotas_livres
            
def filtrar_companhias(servidor_escolhido):
    if servidor_escolhido == 'A':
        return ['B','C']
    
    elif servidor_escolhido == 'B':
        return ['A','C']
    
    elif servidor_escolhido == 'C':
        return ['B','A']

def verifica_rota_escolhida(rota_escolhida, dicionario):
    if rota_escolhida not in filtrar_rotas(dicionario):
        return True
    return False

def verifica_passagem_escolhida(passagens_cliente, passagem_id):
    for p in passagens_cliente:
        if int(p['id_passagem']) == int(passagem_id):
            return True
    return False


# FUNÇÃO PARA FORMATAR A STRING QUE SERÁ RESPONSÁVEL POR EXIBIR AS ROTAS DISPONÍVEIS DE UM SERVIDOR AO CLIENTE
def ver_rotas(dicionario):
    try:
        for rota in dicionario:
            rota_id = int(rota['ID'])
            if 1 <= rota_id <= 29 and rota['assentos_disponiveis'] != 0: 
                print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
                
            elif 30 <= rota_id <= 60 and rota['assentos_disponiveis'] != 0: 
                print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
                
            elif 61 <= rota_id <= 90 and rota['assentos_disponiveis'] != 0: 
                print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
    except:
        pass
    print("\n")

# FUNÇÃO PARA ACESSAR E EXIBIR AS PASSAGENS COMPRADAS POR UM CLIENTE NO MENU DE CANCELAMENTO
def realizar_cancelamento(user_id):
    passagens_cliente = []
    servidores = ['A', 'B', 'C']

    for servidor in servidores:
        try:
            if listar_passagens(servidor):
                for cliente in listar_passagens(servidor):
                    if cliente['id'] == user_id:
                        for info in cliente['passagens']:
                            if info['estaCancelado'] != 1 and info['servidor'] == servidor:
                                passagens_cliente.append(info)
            else:
                print(f"O SERVIDOR {servidor} NÃO RESPONDEU.")
            print("\n")
        except:
            pass

    for info in passagens_cliente:
        print(f"SERVIDOR: {info['servidor']} | ID DA PASSAGEM: {info['id_passagem']} | ROTA: {info['rota']}")
    print("\n")
    if passagens_cliente != []:
        passagem_id = int(input("DIGITE O ID DA PASSAGEM QUE DESEJA CANCELAR (OU DIGITE 0 PARA SAIR):\n"))
        if passagem_id == 0:
            print("\nRETORNANDO AO MENU\n")
            return
        while verifica_passagem_escolhida(passagens_cliente,passagem_id)==False:
            passagem_id = int(input("PASSAGEM INVÁLIDA. DIGITE NOVAMENTE: "))  
        for p in passagens_cliente:
            if int(p['id_passagem']) == passagem_id:
                cancelamento_resultado = cancelar_passagem(p['servidor'], p['id_passagem'], user_id)
                print(f"{cancelamento_resultado}")
    else:
        print("\n\nNEHUMA PASSAGEM ENCONTRADA\n\n")
        return
            