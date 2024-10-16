from flask import Flask, jsonify, request
import requests

from server_utils import carregar_rotas
    
app = Flask(__name__)
    
# Endpoint para consultar trechos da companhia A
@app.route('/trechos', methods=['GET'])
def listar_trechos():
    trechos_filtrados = [rota for rota in carregar_rotas(2)]
    return jsonify(trechos_filtrados)

# Endpoint para comprar um trecho da companhia A
@app.route('/comprar', methods=['POST'])
def reservar_trecho():
    dados = request.get_json()
    trecho_id = dados.get('trecho_id')
    
    # Verifica se o trecho está disponível
    trecho = next((rota for rota in carregar_rotas(2) if rota['ID'] == trecho_id), None)
    if trecho:
        pass
        
        # PROCESSO DE COMPRAR AQUI
        
        return jsonify({"status": "sucesso", "reserva_id": trecho_id, "detalhes": trecho})
    return jsonify({"status": "falha", "mensagem": "Trecho não encontrado"}), 404