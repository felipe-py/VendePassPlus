import socket
import json
from models.client.cliente_utils import * 
import time

# O host antigo era 'servidor_container'
#HOST = '0.0.0.0'
#PORT = 65434

def main():
    while True:
        try:
            # servidor = input("Em qual servidor gostaria de se conectar?\n")
            # while (servidor != '1') and (servidor != '2') and (servidor != '3'):
            #     servidor = input("Por favor, insira um servidor válido (1, 2 ou 3)\n")
            # if servidor == '1':
            #     HOST = '127.0.0.200'
            #     PORT = 65432
            # elif servidor == '2':
            #     HOST = '127.0.0.201'
            #     PORT = 65433
            # elif servidor == '3':
            #     HOST = '127.0.0.202'
            #     PORT = 65434
            # s1 = conectar(HOST, PORT)

            HOST1 = '127.0.0.200'
            PORT1 = 65432

            HOST2 = '127.0.0.201'
            PORT2 = 65433

            HOST3 = '127.0.0.202'
            PORT3 = 65434

            try:
                s1 = conectar(HOST1, PORT1)
            except:
                pass
            try:
                s2 = conectar(HOST2, PORT2)
            except:
                pass
            try:
                s3 = conectar(HOST3, PORT3)
            except:
                pass
            espacos()
            # print("Conectado.")
            espacos()
            # break
        except ConnectionRefusedError:
            print(f"A conexão com o servidor {HOST} na porta {PORT} falhou")
            time.sleep(1)

    # while True:
        user = '0'
        while user == '0':
            try:
                user = login(s1)
            except:
                try:
                    user = login(s2)
                except:
                    user = login(s3)

        if user == "sair":
            break
        elif user:
            while True:
                operacao = menu(user)
                if operacao != '3':
                    if operacao == '1':
                        try:
                            mostrar_rotas(s1)
                        except:
                            pass
                        try:
                            mostrar_rotas(s2)
                        except:
                            pass
                        try:
                            mostrar_rotas(s3)
                        except:
                            pass

                        rotas_a_serem_compradas = []
                        passagens_do_servidor_1 = []
                        passagens_do_servidor_2 = []
                        passagens_do_servidor_3 = []

                        mais_rotas = 's'
                        while mais_rotas.lower() == 'y' or mais_rotas.lower() == 's':
                            rotaID = input("\nInsira o ID da rota desejada ou pressione '0' para cancelar a operação: ")
                            while int(rotaID)<0 or int(rotaID)>90:
                                print(f"Não há rota {rotaID} no sistema. Por favor selecione uma rota valida.\n")
                                rotaID = input("\nInsira o ID da rota desejada ou pressione '0' para cancelar a operação: ")
                            if int(rotaID) == 0:
                                print("saindo")
                                break
                            rotas_a_serem_compradas.append(rotaID)
                            espacos()
                            mais_rotas = input("\nGostaria de comprar mais uma rota?[y/N]\n: ")
                        if int(rotaID) == 0:
                            break
                        for rota in rotas_a_serem_compradas:
                            if int(rota)>60:
                                passagens_do_servidor_3.append(rota)
                            if int(rota)>30:
                                passagens_do_servidor_2.append(rota)
                            else:
                                passagens_do_servidor_1.append(rota)

                        mensagem_server_1 = {
                            'cliente_id': user,
                            #'rotaID': rotaID
                            'rotas_a_serem_compradas': passagens_do_servidor_1
                        }
                        mensagem_server_2 = {
                            'cliente_id': user,
                            #'rotaID': rotaID
                            'rotas_a_serem_compradas': passagens_do_servidor_2
                        }
                        mensagem_server_3 = {
                            'cliente_id': user,
                            #'rotaID': rotaID
                            'rotas_a_serem_compradas': passagens_do_servidor_3
                        }
                        try:
                            comprar_passagem(user, s1, mensagem_server_1)
                        except:
                            pass
                        try:
                            comprar_passagem(user, s2, mensagem_server_2)
                        except:
                            pass
                        try:
                            comprar_passagem(user, s3, mensagem_server_3)
                        except:
                            pass
                    if operacao == '2':
                        print(f"Passagens Compradas por {user}:\n")
                        try:
                            mostrar_passagens(s1, user)
                        except:
                            try: 
                                mostrar_passagens(s2, user)
                            except:
                                mostrar_passagens(s3, user)
                        passagem_a_ser_cancelada = input("\nQual passagem gostaria de cancelar?\n")
                        if passagem_a_ser_cancelada != '0':
                            try:
                                cancelar_compra(s1, passagem_a_ser_cancelada, user)
                            except:
                                pass
                            try:
                                cancelar_compra(s2, passagem_a_ser_cancelada, user)
                            except:
                                pass
                            try:
                                cancelar_compra(s3, passagem_a_ser_cancelada, user)
                            except:
                                pass
                                # try:
                                #     cancelar_compra(s2, passagem_a_ser_cancelada, user)
                                # except:
                                #     cancelar_compra(s3, passagem_a_ser_cancelada, user)
                        # companhia = input(" De qual companhia você deseja cancelar a passagem? '0' para sair\n")
                        # while companhia.lower() != 'a' and companhia.lower() != 'b' and companhia.lower() != 'c' and companhia != '0':
                        #     companhia = input("Por favor selecione uma companhia válida (A,B ou C)\n")
                        # if companhia != '0':
                        #     passagemID = input("Insira o ID da passagem ou pressione '0' para cancelar a operação:\n ")
                        #     if companhia.lower() == 'a':
                        #         cancelar_compra(s1, user)
                        #     elif companhia.lower() == 'b':
                        #         cancelar_compra(s2, user)
                        #     elif companhia.lower() == 'c':
                        #         cancelar_compra(s3, user)
                        # if companhia == '0':
                        #     break
                    try:
                        logout(s1) 
                    except:
                        try:
                            logout(s2)
                        except:
                            logout(s3)
                    break
                if operacao == '3':
                    break
                else:
                    print("Credenciais incorretas, tente novamente.")
                    espacos()

    # user = login(s1)
    #
    # if user:
    #     menu(s1, user)

main()
