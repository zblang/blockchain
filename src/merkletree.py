# -*- coding: utf-8 -*-
# 0. 导入所需要的库
import hashlib
import json
from collections import OrderedDict


class MerkleTree:

    # 类对象初始化
    def __init__(self, list_of_transaction=None):
        self.list_of_transaction = list_of_transaction
        self.past_transaction = OrderedDict()

    # 创建MerkleTree
    # list_of_transaction：所有交易
    # past_transaction： 上一轮交易
    # temp_transaction： 存放父节点的哈希值，作为下一轮哈希的list

    def create_tree(self):

        list_of_transaction = self.list_of_transaction
        past_transaction = self.past_transaction
        temp_transaction = []

        # 遍历list_of_transaction
        for index in range(0, len(list_of_transaction), 2):

            tx = list_of_transaction[index]

            if index + 1 != len(list_of_transaction):
                current_right = list_of_transaction[index + 1]

            else:
                current_right = ''

            current_hash = hashlib.sha256(tx.encode('utf-8'))

            c_hash = current_hash.hexdigest()
            past_transaction[list_of_transaction[index]] = c_hash

            if current_right != '':
                current_right_hash = hashlib.sha256(current_right.encode('utf-8'))
                r_hash = current_right_hash.hexdigest()
                past_transaction[list_of_transaction[index + 1]] = r_hash
                temp_transaction.append(c_hash + r_hash)

            else:
                temp_transaction.append(current_hash.hexdigest())

        if len(list_of_transaction) != 1:
            self.list_of_transaction = temp_transaction
            self.past_transaction = past_transaction

            self.create_tree()

        last_key = list(self.past_transaction.keys())[-1]
        return self.past_transaction[last_key]

    def get_past_transaction(self):
        return self.past_transaction

    def get_root_leaf(self):
        last_key = list(self.past_transaction.keys())[-1]
        return self.past_transaction[last_key]


# if __name__ == "__main__":
#     # Create the new class of MerkleTree
#     tree = MerkleTree()
#
#     # Give list of transaction
#     transaction = ['a', 'b']
#
#     # pass on the transaction list
#     tree.list_of_transaction = transaction
#
#     # Create the Merkle Tree transaction
#     root = tree.create_tree()
#
#     # Retrieve the transaction
#     past_transaction = tree.get_past_transaction()
#
#     # Get the last transaction and print all
#     print("First Example - Even number of transaction Merkle Tree")
#     print('Final root of the tree : ', tree.get_root_leaf())
#     print('test:', root)
#     # indent 缩进
#     print(json.dumps(past_transaction, indent=4))
#     print("-" * 50)
    #
    # # Second example
    # print("Second Example - Odd number of transaction Merkle Tree")
    # tree = MerkleTree()
    # transaction = ['a', 'b', 'c', 'd', 'e']
    # tree.list_of_transaction = transaction
    # tree.create_tree()
    # past_transaction = tree.get_past_transaction()
    # print('Final root of the tree : ', tree.get_root_leaf())
    # print(json.dumps(past_transaction, indent=4))
    # print("-" * 50)
    #
    # # Actual Use Case
    # print("Final Example - Actuall use case of the Merkle Tree")
    #
    # # Declare a transaction - the ground truth
    # ground_truth_Tree = MerkleTree()
    # ground_truth_transaction = ['a', 'b', 'c', 'd', 'e']
    # ground_truth_Tree.list_of_transaction = ground_truth_transaction
    # ground_truth_Tree.create_tree()
    # ground_truth_past_transaction = ground_truth_Tree.get_past_transaction()
    # ground_truth_root = ground_truth_Tree.get_root_leaf()
    #
