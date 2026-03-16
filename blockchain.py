import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
import requests

from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.currentTransactions = []

        self.newBlock(previousHash=1,proof=100)
        self.nodes = set()

    def newBlock(self,proof,previousHash=None):
        block={
            "index":len(self.chain)+1,
            "timestamp":time(),
            "transactions":self.currentTransactions,
            "proof":proof,
            "previousHash":previousHash or self.hash(self.chain[-1]),
        }
        
        self.currentTransactions = []

        self.chain.append(block)
        return block

    def newTransaction(self,sender,recipient,amount):
        self.currentTransactions.append({
            "sender":sender,
            "recipient":recipient,
            "amount":amount,
        })
        return self.lastBlock["index"]+1

    @staticmethod
    def hash(block):
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        return self.chain[-1]
    
    def proofOfWork(self,lastProof):
        proof=0
        while self.validProof(lastProof,proof) is False:
            proof+=1

        return proof
    
    @staticmethod
    def validProof(lastProof,proof):
        guess = f"{lastProof}{proof}".encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4]=="0000"
    
    def registerNode(self,address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    def validChain(self,chain):
        lastBlock = chain[0]
        currentIndex=1

        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f"{lastBlock}")
            print(f"{block}")
            print("\n-----------\n")
            if block["previousHash"] != self.hash(lastBlock):
                return False
            
            if not self.validProof(lastBlock["proof"], block["proof"]):
                return False
            
            lastBlock = block
            currentIndex += 1
        return True
    
    def resolveConflicts(self):
        neighbours = self.nodes
        newChain = None

        maxLength = len(self.chain)

        for node in neighbours:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > maxLength and self.validChain(chain):
                    maxLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True
        return False
    
app = Flask(__name__)

nodeIdentifier = str(uuid4()).replace("-","")

blockchain = Blockchain()

@app.route("/chain",methods=["GET"])
def fullChain():
    response={
        "chain":blockchain.chain,
        "length":len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route("/transaction/new",methods=["POST"])
def new_transaction():
    values=request.get_json()

    required=["sender","recipient","amount"]
    if not all(k in values for k in required):
        return "Missing values", 400
    
    index=blockchain.newTransaction(values["sender"],values["recipient"],values["amount"])

    response={"message":f"Transaction will be added to Block{index}"}
    return jsonify(response), 201

@app.route("/mine", methods=["GET"])
def mine():
    lastBlock=blockchain.lastBlock
    lastProof=lastBlock["proof"]
    proof=blockchain.proofOfWork(lastProof)

    blockchain.newTransaction(
        sender="0",
        recipient=nodeIdentifier,
        amount=1,
    )

    previousHash=blockchain.hash(lastBlock)
    block=blockchain.newBlock(proof,previousHash)

    response={
        "message":"New Block Forged",
        "index":block["index"],
        "transactions":block["transactions"],
        "proof":block["proof"],
        "previousHash":block["previousHash"],
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)