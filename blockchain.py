import hashlib


class Block:
    def __init__(self, previous_hash, sender, receiver, amount):
        self.previous_hash = previous_hash
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.nonce = None
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_string = str(self.previous_hash) + str(self.sender) + str(self.receiver) + str(self.amount) + str(self.nonce)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2

    def create_initial_block(self):
        return Block("0", "initial_sender", "initial_receiver", 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
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