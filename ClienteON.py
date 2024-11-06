from models.client.cliente_utils import *
from models.client.cliente_utils_connection import *

if __name__ == "__main__":
    
    while True:
        print("\n\n=== ESCOLHA A COMPANHIA QUE DESEJA INICIAR AS SUAS COMPRAS ===\n")
        print("(A) COMPANHIA A\n(B) COMPANHIA B\n(C) COMPANHIA C")
        
        servidor_escolhido = input()
        while verifica_escolha_servidor(servidor_escolhido):
            servidor_escolhido = input("SERVIDOR ESCOLHIDO É INVÁLIDO. DIGITE NOVAMENTE: ")
        
        # Verificar se o servidor está ativo
        status = verificar_servidor(servidor_escolhido)
        if status and status['status'] == 'ativo':
            print(f"\nSEJA BEM-VINDO À COMPANHIA AÉREA {servidor_escolhido}")
            break  # Sai do loop, pois o servidor está ativo
        else:
            print(f"Servidor {servidor_escolhido} não está ativo ou não pôde ser alcançado. Tente novamente.")

    # Realizar login
    print("\n\n === REALIZE O LOGIN ===\n\n")
    usuario_id = input("DIGITE O ID: ")
    senha = input("DIGITE A SENHA:")          
    login_resultado = realizar_login(servidor_escolhido, usuario_id, senha)
    
    if login_resultado and login_resultado['status'] == 'sucesso':
        while True:
            print("\n=== Login realizado com sucesso! ===")
            
            print(f"\nBem-vindo(a) {usuario_id}, o que gostaria de fazer?\n\n")
            print("1. Comprar uma passagem")
            print("2. Cancelar uma compra")
            print("3. Sair")

            operacao = input("\n: ")
            while verificar_escolha_menu(operacao):
                operacao = input("OPERAÇÃO INVÁLIDA. DIGITE NOVAMENTE: ")
            
            if operacao == '1':
                    print(f"\n\n ==== ROTAS DISPONÍVEIS PARA A COMPANHIA {servidor_escolhido} ===\n\n")
                    
                    # ver_rotas(listar_rotas(servidor_escolhido))
                    rotas_para_compra = []
                    rotas_servidor_A = []
                    rotas_servidor_B = []
                    rotas_servidor_C = []
                    
                    try:
                        ver_rotas(listar_rotas('A'))
                    except:
                        pass    
                    try:
                        ver_rotas(listar_rotas('B'))
                    except:
                        pass    
                    try:
                        ver_rotas(listar_rotas('C'))
                    except:
                        pass    

                    r = int(input("INDIQUE A ROTA QUE DESEJA COMPRAR (0 PARA SAIR): "))
                    if r == '0':
                        break
                    elif (r<0) or (r>90):
                        r = int(input("POR FAVOR SELECIONE UMA OPÇÃO VÁLIDA: "))
                    
                    if (r>60):
                        try:
                           comprar_passagem('C', usuario_id, [r] )
                        except:
                            print("Falha ao comprar em C.")
                            pass
                    elif (r>29):
                        try:
                           comprar_passagem('B', usuario_id, [r] )
                        except:
                            print("Falha ao comprar em B.")
                            pass
                    else:
                        try:
                           comprar_passagem('A', usuario_id, [r] )
                        except:
                            print("Falha ao comprar em A.")
                            pass

                        
            elif operacao == '2':
                realizar_cancelamento(usuario_id)
                    
            elif operacao == '3':
                print("Saindo...")
                break
            
    else:
        print("Falha no login:", login_resultado.get('mensagem', 'Erro desconhecido'))
        
