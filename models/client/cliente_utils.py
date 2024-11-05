from models.client.cliente_utils_connection import listar_rotas, comprar_passagem, cancelar_passagem, listar_passagens

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
    if passagem_id not in passagens_cliente:
        return True
    return False

def ver_rotas(dicionario):
    for rota in dicionario:
        rota_id = int(rota['ID'])
        if 1 <= rota_id <= 29 and rota['assentos_disponiveis'] != 0: 
            print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
            
        elif 30 <= rota_id <= 60 and rota['assentos_disponiveis'] != 0: 
            print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
            
        elif 61 <= rota_id <= 90 and rota['assentos_disponiveis'] != 0: 
            print(f"=> ID: {rota['ID']} | Trecho: {rota['trecho']} | Assentos Disponíveis: {rota['assentos_disponiveis']}")
            
        print('\n')

def realizar_compra(servidor_escolhido,usuario_id):
    if listar_rotas(servidor_escolhido):
        rotas_escolhidas = []
        n_rotas_comprar = int(input(f"Digite o numero de rotas que irá comprar da companhia {servidor_escolhido}:"))
        
        for i in range(n_rotas_comprar):
            rota_id = input("DIGITE O ID DA ROTA QUE DESEJA COMPRAR: ")
            while verifica_rota_escolhida(rota_id,listar_rotas(servidor_escolhido)):
                rota_id = input("ID INVÁLIDO. DIGITE NOVAMENTE: ")
            rotas_escolhidas.append(rota_id)
    
    compra_resultado = comprar_passagem(servidor_escolhido, usuario_id, rotas_escolhidas)
    print("Resultado da compra:", compra_resultado)

def realizar_cancelamento(servidor, user_id):
    passagens_cliente = []
    
    if listar_passagens(servidor):
        for cliente in listar_passagens(servidor):
            if cliente['id'] == user_id:
                for info in cliente['passagens']:
                    if info['estaCancelado'] != 1 and info['servidor'] == servidor:
                        print(f"ID DA PASSAGEM: {info['id_passagem']} | ROTA: {info['rota']} | SERVIDOR: {info['servidor']}")
                        passagens_cliente.append(info['id_passagem'])
    
    if passagens_cliente != []:
        passagem_id = int(input("DIGITE O ID DA PASSAGEM QUE DESEJA CANCELAR:"))
        while verifica_passagem_escolhida(passagens_cliente,passagem_id):
            passagem_id = int(input("PASSAGEM INVÁLIDA. DIGITE NOVAMENTE: "))  
    
    else:
        print("\n\nNEHUMA PASSAGEM ENCONTRADA\n\n")
        return
              
    cancelamento_resultado = cancelar_passagem(servidor, passagem_id,user_id)
    print("Resultado do cancelamento:", cancelamento_resultado)
    
    