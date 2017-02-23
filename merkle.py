from hashlib import sha256
from math import log
import codecs

hash_function = sha256


class MerkleError(Exception):
    pass


class Node(object):
    """Each node has, as attributes, references to left (l) and right (r) child nodes, parent (p),
    and sibling (sib) node. It can also be aware of whether it is on the left or right hand side (side).
    data is hashed automatically by default, but does not have to be, if prehashed param is set to True.
    """
    __slots__ = ['l', 'r', 'p', 'sib', 'side', 'val']

    def __init__(self, data, prehashed=False):
        if prehashed:
            self.val = data
        else:
            self.val = hash_function(data).digest()
        self.l = None
        self.r = None
        self.p = None
        self.sib = None
        self.side = None

    def __repr__(self):
        return "Val: <" + str(codecs.encode(self.val, 'hex_codec')) + ">"


class MerkleTree(object):
    """A Merkle tree implementation.  Added values are stored in a list until the tree is built.
    A list of data elements for Node values can be optionally supplied to the constructor.
    Data supplied to the constructor is hashed by default, but this can be overridden by
    providing prehashed=True in which case, node values should be hex encoded.
    """
    def __init__(self, leaves=[], prehashed=False, raw_digests=False):
        if prehashed and raw_digests:
            self.leaves = [Node(leaf, prehashed=True) for leaf in leaves]
        elif prehashed:
            self.leaves = [Node(codecs.decode(leaf, 'hex_codec'), prehashed=True) for leaf in leaves]
        else:
            self.leaves = [Node(leaf) for leaf in leaves]
        self.root = None

    def __eq__(self, obj):
        return (self.root.val == obj.root.val) and (self.__class__ == obj.__class__)

    def add(self, data):
        """Add a Node to the tree, providing data, which is hashed automatically.
        """
        self.leaves.append(Node(data))

    def add_hash(self, value):
        """Add a Node based on a precomputed, hex encoded, hash value.
        """
        self.leaves.append(Node(codecs.decode(value, 'hex_codec'), prehashed=True))

    def clear(self):
        """Clears the Merkle Tree by releasing the Merkle root and each leaf's references, the rest
        should be garbage collected.  This may be useful for situations where you want to take an existing
        tree, make changes to the leaves, but leave it uncalculated for some time, without node
        references that are no longer correct still hanging around. Usually it is better just to make
        a new tree.
        """
        self.root = None
        for leaf in self.leaves:
            leaf.p, leaf.sib, leaf.side = (None, ) * 3

    def build(self):
        """Calculate the merkle root and make references between nodes in the tree.
        """
        if not self.leaves:
            raise MerkleError('The tree has no leaves and cannot be calculated.')
        layer = self.leaves[::]
        while len(layer) != 1:
            layer = self._build(layer)
        self.root = layer[0]
        return self.root.val

    def build_fun(self, layer=None):
        """Calculate the merkle root and make references between nodes in the tree.
        Written in functional style purely for fun.
        """
        if not layer:
            if not self.leaves:
                raise MerkleError('The tree has no leaves and cannot be calculated.')
            layer = self.leaves[::]
        layer = self._build(layer)
        if len(layer) == 1:
            self.root = layer[0]
        else:
            self.build_fun(layer=layer)
        return self.root.val

    def _build(self, leaves):
        """Private helper function to create the next aggregation level and put all references in place.
        """
        new, odd = [], None
        # check if even number of leaves, promote odd leaf to next level, if not
        if len(leaves) % 2 == 1:
            odd = leaves.pop(-1)
        for i in range(0, len(leaves), 2):
            newnode = Node(leaves[i].val + leaves[i + 1].val)
            newnode.l, newnode.r = leaves[i], leaves[i + 1]
            leaves[i].side, leaves[i + 1].side, leaves[i].p, leaves[i + 1].p = 'L', 'R', newnode, newnode
            leaves[i].sib, leaves[i + 1].sib = leaves[i + 1], leaves[i]
            new.append(newnode)
        if odd:
            new.append(odd)
        return new

    def get_chain(self, index):
        """Assemble and return the chain leading from a given node to the merkle root of this tree.
        """
        chain = []
        this = self.leaves[index]
        chain.append((this.val, 'SELF'))
        while this.p:
            chain.append((this.sib.val, this.sib.side))
            this = this.p
        chain.append((this.val, 'ROOT'))
        return chain

    def get_all_chains(self):
        """Assemble and return a list of all chains for all leaf nodes to the merkle root.
        """
        return [self.get_chain(i) for i in range(len(self.leaves))]

    def get_hex_chain(self, index):
        """Assemble and return the chain leading from a given node to the merkle root of this tree
        with hash values in hex form
        """
        return [(codecs.encode(i[0], 'hex_codec'), i[1]) for i in self.get_chain(index)]

    def get_all_hex_chains(self):
        """Assemble and return a list of all chains for all nodes to the merkle root, hex encoded.
        """
        return [[(codecs.encode(i[0], 'hex_codec'), i[1]) for i in j] for j in self.get_all_chains()]

    def _get_whole_subtrees(self):
        """Returns an array of nodes in the tree that have balanced subtrees beneath them,
        moving from left to right.
        """
        subtrees = []
        loose_leaves = len(self.leaves) - 2**int(log(len(self.leaves), 2))
        the_node = self.root
        while loose_leaves:
            subtrees.append(the_node.l)
            the_node = the_node.r
            loose_leaves = loose_leaves - 2**int(log(loose_leaves, 2))
        subtrees.append(the_node)
        return subtrees

    def add_adjust(self, data, prehashed=False):
        """Add a new leaf, and adjust the tree, without rebuilding the whole thing.
        """
        subtrees = self._get_whole_subtrees()
        new_node = Node(data, prehashed=prehashed)
        self.leaves.append(new_node)
        for node in reversed(subtrees):
            new_parent = Node(node.val + new_node.val)
            node.p, new_node.p = new_parent, new_parent
            new_parent.l, new_parent.r = node, new_node
            node.sib, new_node.sib = new_node, node
            node.side, new_node.side = 'L', 'R'
            new_node = new_node.p
        self.root = new_node


def check_chain(chain):
    """Verify a merkle chain to see if the Merkle root can be reproduced.
    """
    link = chain[0][0]
    for i in range(1, len(chain) - 1):
        if chain[i][1] == 'R':
            link = hash_function(link + chain[i][0]).digest()
        elif chain[i][1] == 'L':
            link = hash_function(chain[i][0] + link).digest()
        else:
            raise MerkleError('Link %s has no side value: %s' % (str(i), str(codecs.encode(chain[i][0], 'hex_codec'))))
    if link == chain[-1][0]:
        return link
    else:
        raise MerkleError('The Merkle Chain is not valid.')


def check_hex_chain(chain):
    """Verify a merkle chain, with hashes hex encoded, to see if the Merkle root can be reproduced.
    """
    return codecs.encode(check_chain([(codecs.decode(i[0], 'hex_codec'), i[1]) for i in chain]), 'hex_codec')


def join_chains(low, high):
    """Join two hierarchical merkle chains in the case where the root of a lower tree is an input
    to a higher level tree. The resulting chain should check out using the check functions. Use on either
    hex or binary chains.
    """
    if not low[-1][0] == high[0][0]:
        raise MerkleError('The two chains do not connect.')
    return low[:-1] + high[1:]
