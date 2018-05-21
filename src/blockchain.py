# -*- coding: utf-8 -*-
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import merkletree
import requests
from flask import Flask, jsonify, request
# To do:
# 用脚本的话，挖到矿时，应该直接更新区块链而不是手动更新
# Merkel tree


class Blockchain:
    def __init__(self):
        self.current_transactions = []  #
        self.chain = []
        self.nodes = set()
        self.memory_pool = []
        self.merkle_root = ''
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        加入新节点

        :param address: 节点的地址. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        通过验证每个区块的proof，判断给予的区块链是否有效

        :param chain: 某个区块链
        :return: 有效返回True，否则False
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        共识机制：通过相信最长链解决冲突

        :return: 若被替换则为True，否则为False
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    #
    def new_child_block(self):

        child_block = {
            # 'miner': ,
            'pool': self.memory_pool,
        }
        self.memory_pool = []
        # self.chain.append(child_block)
        return child_block

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm  用于工作证明的解
        :param previous_hash: Hash of previous Block                  前一块的hash
        :return: New Block
        """
        # 更新merkle_root
        self.get_merkle_root()

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'pool': self.memory_pool,
            'merkle_root': self.merkle_root,
        }
        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def get_merkle_root(self):
        tree = merkletree.MerkleTree()
        tree.list_of_transaction = str(self.current_transactions)
        print(tree.create_tree())
        self.merkle_root = tree.create_tree()

    def new_transaction(self, sender, recipient, amount):
        """
        创建一个置于下个区块的交易

        :param sender: 发送者的地址
        :param recipient: 接收者的地址
        :param amount: 交易的硬币数量
        :return: 返回会承载这个交易的区块索引
        """
        if sender == '0':
            self.current_transactions.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            })
        elif len(self.current_transactions) <= 10:
            self.current_transactions.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            })
            print('length of current_transactions: ' + str(len(self.current_transactions)))
        else:
            self.memory_pool.append({
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            })

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        计算区块的SHA256值

        :param block: 区块
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        基于工作量证明的算法

         1. 找到一个数字p' 使得 hash(pp') 以四位零开头
         2. p是前一个proof，p'是新的proof

        :param last_block: <dict> 前一个区块
        :return: <int> 当前proof
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        验证 Proof

        :param last_proof: <int> 前一个proof
        :param proof: <int> 当前 Proof
        :param last_hash: <str> 前一块的hash
        :return: <bool> 正确为True，错误为False

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"


# 节点实例化
app = Flask(__name__)

# 给节点生成一个独一无二的地址
node_identifier = str(uuid4()).replace('-', '')

# 区块链实例化
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # 使用工作量证明机制得到解
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # 找到解得有奖励
    # 发送者为“0”来标识这个交易为创币交易
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=50,
    )

    # 把新块连到区块链中
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    # 找到块之后，
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    if len(blockchain.memory_pool) == 0:
        return jsonify(response), 200
    child_block = blockchain.new_child_block()
    response = {
        'index': block['index'],
        'message': "New Block Forged",
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions'],
        'child_block': child_block['pool'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 检查发送过来的json数据
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一笔新的交易
    # index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    if len(blockchain.memory_pool) == 0:
        response = {'message': f'Transaction will be added to next Block'}
    else:
        response = {'message': f'Transaction will be added to pool'}
    return jsonify(response), 201


@app.route('/chain/pool', methods=['GET'])
def pool():
    response = {
        'amount': len(blockchain.memory_pool),
        'transaction': blockchain.memory_pool
    }
    return jsonify(response), 202


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
