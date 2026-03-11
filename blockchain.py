import hashlib
import json
from time import time
from uuid import uuid4

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