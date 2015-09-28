import pytest
import json
from merkle import *


test_tree = MerkleTree()
for i in 'abcd':
    test_tree.add(i)

test_tree2 = MerkleTree([i for i in 'abcd'])
root = test_tree.build()
test_tree2.build()
test_node = test_tree.leaves[0]
test_chain = test_tree.get_chain(0)
test_hex_chain = test_tree.get_hex_chain(0)


def test0():
    assert root.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test1():
    assert test_tree.root.val.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test2():
    assert check_chain(test_chain) == "\x14\xed\xe5\xe8\xe9z\xd97#'r\x8fP\x99\xb9V\x04\xa3\x95\x93\xca\xc3\xbd8\xa3C\xadv R\x13\xe7"


def test3():
    assert check_hex_chain(test_hex_chain) == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


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


def test10():
    assert test_tree == test_tree2


def test11():
    t11 = MerkleTree(['14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'], prehashed=True)
    assert t11.build().encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test12():
    mod_chain = test_chain[::]
    mod_chain[1] = test_chain[1][0], ''
    try:
        check_chain(mod_chain)
    except MerkleError, e:
        assert e.message == 'Link 1 has no side value: 3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'
        return
    raise AssertionError('Test 12: Hash chain validated when it should not have.')


def test13():
    toptree = MerkleTree([i for i in 'abc'])
    toptree.add_hash('14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7')
    toproot = toptree.build()
    topchain = toptree.get_chain(3)
    joined_chain = join_chains(test_chain, topchain)
    assert check_chain(joined_chain) == toproot


def test14():
    mod_chain = test_chain[::]
    mod_chain[1] = test_chain[1][0][:-1] + 'p', test_chain[1][1]
    try:
        check_chain(mod_chain)
    except MerkleError, e:
        assert e.message == 'The Merkle Chain is not valid.'
        return
    raise AssertionError('Test 14: Hash chain validated when it should not have.')


def test15():
    tree_15 = MerkleTree([i for i in 'abcd'])
    root = tree_15.build().encode('hex')
    assert root == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'
    tree_15.clear()
    assert tree_15.root is None
    assert tree_15.leaves[0].p is None


def test16():
    all_chains = test_tree.get_all_hex_chains()
    assert json.dumps(all_chains) == """\
[[["ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "SELF"], \
["3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "R"], \
["bffe0b34dba16bc6fac17c08bac55d676cded5a4ade41fe2c9924a5dde8f3e5b", "R"], \
["14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT"]], \
[["3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "SELF"], \
["ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "L"], \
["bffe0b34dba16bc6fac17c08bac55d676cded5a4ade41fe2c9924a5dde8f3e5b", "R"], \
["14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT"]], \
[["2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "SELF"], \
["18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "R"], \
["e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a", "L"], \
["14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT"]], \
[["18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "SELF"], \
["2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "L"], \
["e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a", "L"], \
["14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT"]]]\
"""


def test17():
    tree_17 = MerkleTree()
    try:
        tree_17.build()
    except MerkleError, e:
        assert e.message == 'The tree has no leaves and cannot be calculated.'


def test18():
    test_tree3 = MerkleTree([i for i in 'abcd'])
    test_tree3.build_fun()
    assert test_tree == test_tree3
