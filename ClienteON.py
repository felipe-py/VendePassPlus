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
                    
                    ver_rotas(listar_rotas(servidor_escolhido))
                    
                    print(f"=== DESEJA COMPRAR SUA PASSAGEM NA COMPANHIA {servidor_escolhido} OU VER ROTAS DE OUTRAS COMPANHIAS? ===")
                    print(f"(1) Continuar na companhia {servidor_escolhido}\n(2) Ver rotas de outras companhias")
                    
                    escolha_companhia = input()
                    while verificar_escolha_companhia_compra(escolha_companhia):
                        escolha_companhia = input("OPERAÇÃO ONVÁLIDA. DIGITE NOVAMENTE: ")
                        
                    if escolha_companhia == '1':
                        realizar_compra(servidor_escolhido,usuario_id)
                    
                    elif escolha_companhia == '2':
                        print("\n\n====== PASSAGENS DISPONÍVEIS NAS COMPANHIAS PARCEIRAS ======")
                        outras_companhias = filtrar_companhias(servidor_escolhido)
                        
                        print(f"=> ROTAS DA COMPANHIA {outras_companhias[0]} <=")
                        ver_rotas(listar_rotas(outras_companhias[0]))
                        
                        print(f"=> ROTAS DA COMPANHIA {outras_companhias[1]} <=")
                        ver_rotas(listar_rotas(outras_companhias[1]))

                        print("\n\n===== DESEJA REALIZAR A COMPRA EM QUAL SERVIDOR ======")
                        print(f"({outras_companhias[0]}) Companhia {outras_companhias[0]}\n({outras_companhias[1]}) Companhia {outras_companhias[1]}")
                
                        novo_servidor_escolhido = input()
                        while verifica_escolha_servidor(novo_servidor_escolhido):
                            novo_servidor_escolhido = input("SERVIDOR ESCOLHIDO É INVÁLIDO. DIGITE NOVAMENTE: ")

                        realizar_compra(novo_servidor_escolhido, usuario_id)
                        
            elif operacao == '2':
                realizar_cancelamento(servidor_escolhido, usuario_id)
            
            elif operacao == '3':
                print("Saindo...")
                break
            
    else:
        print("Falha no login:", login_resultado.get('mensagem', 'Erro desconhecido'))
        