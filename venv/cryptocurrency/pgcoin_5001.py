import datetime  #pegar data exata
import hashlib   #pra gerar hash
import json      #pra leitura dos dados em json 
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Parte 1, criando o Blockchain

class Blockchain: 
    def __init__(self):
        self.chain = []   #Blockchain
        self.transactions = [] #Transações 
        self.create_block(proof = 1, previous_hash='0')
        self.nodes = set() #conjunto nós
        
    #Método de criação do block    
    def create_block(self, proof, previous_hash):
        block = { 
            'index': len(self.chain) + 1,               #Pegando o indice
            'timestamp': str(datetime.datetime.now()),  #Pegando a hora e convertendo para texto
            'proof': proof,                             #Equivalente ao nounce
            'previous_hash': previous_hash,             #Hash do block anterior
            'transactions': self.transactions           #lista de transações incluidas no block
        }
        self.transactions = []
        self.chain.append(block)                        #Inserindo no Blockchain o block
        return block                                    #Retornando o block criado
     
    #Método para retornar o block anerior
    def get_previous_block(self): 
        return self.chain[-1]
    
    #Método de mineração 
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            #Produzindo um hash 
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
                             #hash sha256   -> Transfomando em Texto -> nível de dificuldade -> e gerando em hexadecimal
            
            #verificando se atendeu o nível de dificuldade
            if hash_operation[:4] == '0000':
                check_proof = True
            else: 
                new_proof += 1
        return new_proof 
    
    
    #Método que transforma o block em arquivo json, e retorna o hash.
    def hash(self, block):
        #Transformando o block e json, e ordenando pela chave
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #Verificando a integridade do BlockChain
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            
            #Validando o hash anterior
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            # Validando se o hash é valido
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index +=1
        
        #BlockChain Integro!
        return True
    
    #Função para adicionar transações
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    #Adicionando nós a rede
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #Substituindo o blockcahin
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

        
        

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()  #Instanciando o objeto BlockChain

#Página para mineração do blockchain
@app.route('/mine_block', methods = ['GET'])        
def mine_block():
    previous_block = blockchain.get_previous_block() #Obtendo o ultimo block gerado
    previous_proof = previous_block['proof']         #obtendo o ultimo proof do block gerado
    proof = blockchain.proof_of_work(previous_proof) #obtendo um proof atual
    previous_hash = blockchain.hash(previous_block)  #obtendo o ultimo hash do block gerado
    blockchain.add_transaction(sender=node_address, receiver='Pedro Torres', amount=5) #Adicionando uma transação 
    
    #Criando o block
    block = blockchain.create_block(proof, previous_hash)
    
    #Exibindo o block minerado
    response = {'message' : 'Parabéns você minerou um bloco!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transaction': block['transactions']
                }
    return jsonify(response, 200)


#Página para visualizar todo o blockchain
@app.route('/get_chain', methods = ['GET']) 
def get_chain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)
                }
    return jsonify(response, 200)


#Página de verificação de integridade da blockchain
@app.route('/is_valid', methods = ['GET']) 
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'Tudo certo, o blockchain está integro'}
    else: 
        response = {'message' : 'O blockchain não está integro'}
    return jsonify(response, 200)


#Adicionando transacoes
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Alguns elementos estao faltando', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'messege': f'Esta transacao sera adicionada ao bloco {index}'}
    return jsonify(response), 201

#Conectando os nós
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'Vazio', 400
    for node in nodes:
        blockchain.add_node(node)
    reponse = {
        'message': 'Todos nos conectados, blockchain contem os seguintes nos:',
        'total_nodes' : list(blockchain.nodes)
    }
    return jsonify(reponse), 201


#método para substiruir o blockchain caso ele seja menor
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_raplaced = blockchain.replace_chain()
    if is_chain_raplaced:
        response = {
            'message': 'Os nos tinham cadeias diferentes e foram sunstituidos',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Tudo cero, nao houve substituicao',
            'atual_chain': blockchain.chain
        }
    return jsonify(response), 201
    

app.run(host= '0.0.0.0', port=5001)
