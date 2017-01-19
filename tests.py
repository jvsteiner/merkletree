import pytest
from merkle import *


@pytest.fixture
def tree():
    tree = MerkleTree([i for i in 'abcd'])
    tree.build()
    return tree


@pytest.fixture
def node(tree):
    return tree.leaves[0]


@pytest.fixture
def chain(tree):
    return tree.get_chain(0)


@pytest.fixture
def hexchain(tree):
    return tree.get_hex_chain(0)


def test_root(tree):
    assert tree.root.val.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test_chain(chain):
    assert check_chain(chain) == "\x14\xed\xe5\xe8\xe9z\xd97#'r\x8fP\x99\xb9V\x04\xa3\x95\x93\xca\xc3\xbd8\xa3C\xadv R\x13\xe7"


def test_hexchain(hexchain):
    assert check_hex_chain(hexchain) == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test_traversal(node):
    assert node.p.r.sib == node


def test_xtraversal(node):
    assert node.p.r != node


def test_none_traversal(node):
    assert node.p.p.p is None


def test_expected_parent(node):
    assert node.p.p.val.encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test_expected_sibling(node):
    assert node.sib.val.encode('hex') == '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'


def test_node_val(node):
    assert node.val.encode('hex') == 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'


def test_prehashed():
    other_tree = MerkleTree(['14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'], prehashed=True)
    assert other_tree.build().encode('hex') == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'


def test_modified(chain):
    mod_chain = chain[::]
    mod_chain[1] = chain[1][0], ''
    with pytest.raises(MerkleError) as excinfo:
        check_chain(mod_chain)
    assert excinfo.value.message == 'Link 1 has no side value: 3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'


def test_join(chain):
    toptree = MerkleTree([i for i in 'uio'])
    toptree.add_hash('14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7')
    toproot = toptree.build()
    topchain = toptree.get_chain(3)
    joined_chain = join_chains(chain, topchain)
    assert check_chain(joined_chain) == toproot


def test_invalid_join(chain):
    toptree = MerkleTree([i for i in 'uio'])
    toptree.build()
    topchain = toptree.get_chain(2)
    with pytest.raises(MerkleError) as excinfo:
        joined_chain = join_chains(chain, topchain)
    assert excinfo.value.message == 'The two chains do not connect.'


def test_invalid_chain(chain):
    mod_chain = chain[::]
    mod_chain[1] = chain[1][0][:-1] + 'p', chain[1][1]
    with pytest.raises(MerkleError) as excinfo:
        check_chain(mod_chain)
    assert excinfo.value.message == 'The Merkle Chain is not valid.'


def test_clear(tree):
    tree = MerkleTree([i for i in 'abcd'])
    root = tree.build().encode('hex')
    assert root == '14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7'
    tree.clear()
    assert tree.root is None
    assert len(tree.leaves) == 4


def test_full_output(tree):
    all_chains = tree.get_all_hex_chains()
    assert all_chains == [
        [
            ("ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "SELF"),
            ("3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "R"),
            ("bffe0b34dba16bc6fac17c08bac55d676cded5a4ade41fe2c9924a5dde8f3e5b", "R"),
            ("14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT")
        ], [
            ("3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "SELF"),
            ("ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "L"),
            ("bffe0b34dba16bc6fac17c08bac55d676cded5a4ade41fe2c9924a5dde8f3e5b", "R"),
            ("14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT")
        ], [
            ("2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "SELF"),
            ("18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "R"),
            ("e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a", "L"),
            ("14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT")
        ], [
            ("18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4", "SELF"),
            ("2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "L"),
            ("e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a", "L"),
            ("14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7", "ROOT")
        ]
    ]


def test_no_leaves():
    tree = MerkleTree()
    with pytest.raises(MerkleError) as excinfo:
        tree.build()
    assert excinfo.value.message == 'The tree has no leaves and cannot be calculated.'


def test_equality(tree):
    other_tree = MerkleTree([i for i in 'abcd'])
    other_tree.build_fun()
    assert tree == other_tree


def test_clear_and_rebuild(tree):
    other_tree = MerkleTree([i for i in 'abc'])
    other_tree.build()
    other_tree.clear()
    other_tree.add('d')
    other_tree.build()
    assert other_tree == tree


def test_add_adjust():
    inputs = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(1, len(inputs) + 1, 1):
        control_tree = MerkleTree([j for j in inputs[0:i]])
        control_tree.build()
        test_tree = MerkleTree([inputs[0]])
        test_tree.build()
        for k in range(1, i, 1):
            test_tree.add_adjust(inputs[k])
        assert control_tree == test_tree
        assert control_tree.get_all_chains() == test_tree.get_all_chains()


def test_add_adjust_prehashed():
    inputs = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(1, len(inputs) + 1, 1):
        control_tree = MerkleTree([hash_function(j).hexdigest() for j in inputs[0:i]], prehashed=True)
        control_tree.build()
        test_tree = MerkleTree([hash_function(inputs[0]).hexdigest()], prehashed=True)
        test_tree.build()
        for k in range(1, i, 1):
            test_tree.add_adjust(hash_function(inputs[k]).digest(), prehashed=True)
        assert control_tree == test_tree
        assert control_tree.get_all_chains() == test_tree.get_all_chains()
