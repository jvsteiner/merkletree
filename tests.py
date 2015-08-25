import json
import pytest
from merkle import *


test_tree = MerkleTree()
for i in 'abcd':
    test_tree.add(i)
test_tree.calc()
test_node = test_tree.leaves[2]
test_chain = test_node.chain()
test_hex_chain = json.dumps(test_node.hex_chain())


def test1():
    assert test_tree.root.val.encode('hex') == "14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7"


def test2():
    assert check_chain(test_chain) == ('success', '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7')


def test3():
    assert check_hex_chain(json.loads(test_hex_chain)) == ('success', '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7')
