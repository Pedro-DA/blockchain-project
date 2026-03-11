import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.currentTransactions = []

        self.newBlock(previousHash=1,proof=100)

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
    def validMethod(lastProof,proof):
        guess = f"{lastProof}{proof}".encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4]=="0000"
    
app = Flask(__name__)

nodeIdentifier = str(uuid4()).replace("-","")

Blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    return "We'll mine a new block"

@app.route("/transactions/new",methods=["POST"])
def newTransaction():
    return "We'll add a new transaction"

@app.route("/chain",methods=["GET"])
def fullChain():
    response={
        "chain":Blockchain.chain,
        "length":len(Blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)