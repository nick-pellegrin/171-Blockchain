import hashlib


class Block:
    def __init__(self, previous_hash, sender, receiver, amount, time):
        self.previous_hash = previous_hash
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.nonce = 0
        self.hash = self.calculate_hash()
        self.time = time


    def calculate_hash(self):
        hash_string = str(self.previous_hash) + str(self.sender) + str(self.receiver) + "$" + str(self.amount) + str(self.nonce)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        # bin_hash = "{0:08b}".format(int(encoded[:2], 16))
        # while self.hash[:difficulty] != "0" * difficulty:
        while int(self.hash[0], 16) >= 4:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.chain[0].hash = self.chain[0].previous_hash
        self.difficulty = 1

    def create_genesis_block(self):
        return Block("0" * 64, "genesis_sender", "genesis_receiver", 0, 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        # new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def get_balance(self, client):
        balance = 10
        for block in self.chain:
            if block.sender == client:
                balance -= block.amount
            if block.receiver == client:
                balance += block.amount
        return balance
    
    def get_chain(self):
        transactions = []
        for block in self.chain:
            transactions.append((block.sender, block.receiver, block.amount, block.nonce, block.previous_hash, block.time))
        return transactions
    
