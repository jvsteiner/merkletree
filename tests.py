import json
import pytest
from merkle import *


test_tree = MerkleTree()
for i in 'abcd':
    test_tree.add(i)

root = test_tree.build()
test_node = test_tree.leaves[0]
test_chain = test_tree.get_chain(0)
test_hex_chain = json.dumps(test_tree.get_hex_chain(0))


def test0():
    assert root == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test1():
    assert test_tree.root.val.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test2():
    assert check_chain(test_chain) == "\x14\xed\xe5\xe8\xe9z\xd97#'r\x8fP\x99\xb9V\x04\xa3\x95\x93\xca\xc3\xbd8\xa3C\xadv R\x13\xe7"


def test3():
    assert check_hex_chain(json.loads(test_hex_chain)) == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test4():
    assert test_node.p.r.sib == test_node


def test5():
    assert test_node.p.r != test_node


def test6():
    assert test_node.p.p.p is None


def test7():
    assert test_node.p.p.val.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test8():
    assert test_node.sib.val.encode('hex') == '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'


def test9():
    assert test_node.val.encode('hex') == 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
