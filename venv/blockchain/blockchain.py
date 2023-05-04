import datetime  #pegar data exata
import hashlib   #pra gerar hash
import json      #pra leitura dos dados em json 
from flask import Flask, jsonify


# Parte 1, criando o Blockchain

class Blockchain: 
    def __init__(self):
        self.chain = []   #Blockchain
        self.create_block(proof = 1, previous_hash='0')
        
        
    #Método de criação do block    
    def create_block(self, proof, previous_hash):
        block = { 
            'index': len(self.chain) + 1,               #Pegando o indice
            'timestamp': str(datetime.datetime.now()),  #Pegando a hora e convertendo para texto
            'proof': proof,                             #Equivalente ao nounce
            'previous_hash': previous_hash              #Hash do block anterior
        }
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
        
        

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain()  #Instanciando o objeto BlockChain

#Página para mineração do blockchain
@app.route('/mine_block', methods = ['GET'])        
def mine_block():
    previous_block = blockchain.get_previous_block() #Obtendo o ultimo block gerado
    previous_proof = previous_block['proof']         #obtendo o ultimo proof do block gerado
    proof = blockchain.proof_of_work(previous_proof) #obtendo um proof atual
    previous_hash = blockchain.hash(previous_block)  #obtendo o ultimo hash do block gerado
    
    #Criando o block
    block = blockchain.create_block(proof, previous_hash)
    
    #Exibindo o block minerado
    response = {'message' : 'Parabéns você minerou um bloco!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']
                }
    return jsonify(response, 200)


#Página para visualizar todo o blockchain
@app.route('/get_chain', methods = ['GET']) 
def get_chain():
    response = {'chain' : blockchain.chain,
                'lenght' : len(blockchain.chain)
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
    

app.run(host= '0.0.0.0', port=5000)
