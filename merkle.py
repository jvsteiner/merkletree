import json
from hashlib import sha256

hash_function = sha256


class Node(object):
    """Each node has references to left and right child nodes, parent, and sibling.
    It can also be aware of whether it is on the left or right hand side.
    """
    def __init__(self, data):
        self.l = None
        self.r = None
        self.val = hash_function(data).digest()
        # self.val = data
        self.p = None
        self.sib = None
        self.side = None

    def __repr__(self):
        return "Val: <" + str(self.val.encode('hex')) + ">"


class MerkleTree(object):
    """A Merkle tree implementation.  Added values are stored in a list until the tree is built.
    """
    def __init__(self, leaves=[]):
        self.leaves = [Node(leaf) for leaf in leaves]
        self.root = None

    def __eq__(self, obj):
        return self.root.val == obj.root.val

    def add(self, data):
        """Add a value to the tree, it's value is hashed automatically
        """
        self.leaves.append(Node(data))

    def add_hash(self, _hash):
        """Add a precomputed hash value, hex format required/assumed.
        """
        new_node = Node('temp')
        new_node.val = _hash.decode('hex')
        self.leaves.append(new_node)

    def clear(self):
        """Releases the Merkle root, and node references are garbage collected
        """
        self.root = None

    def build(self):
        """Calculate the merkle root and make node-node references in the whole tree.
        """
        if not self.leaves:
            raise AssertionError('No leaves')
        layer = self.leaves[::]
        while 1:
            layer = self._build(layer)
            if len(layer) == 1:
                self.root = layer[0]
                break
        return self.root.val.encode('hex')

    def _build(self, leaves):
        """Private helper function to create the next aggregation level and put all references in place
        """
        new, odd = [], None
        # ensure even number of leaves
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
        """Assemble and return the chain leading from a given node to the merkle root of this tree
        """
        chain = []
        this = self.leaves[index]
        chain.append((this.val, 'SELF'))
        while 1:
            if not this.p:
                chain.append((this.val, 'ROOT'))
                break
            else:
                chain.append((this.sib.val, this.sib.side))
                this = this.p
        return chain

    def get_all_chains(self):
        """Assemble and return chains for all nodes to the merkle root
        """
        return [self.get_chain(i) for i in range(len(self.leaves))]

    def get_hex_chain(self, index):
        """Assemble and return the chain leading from a given node to the merkle root of this tree
        with hash values in hex form
        """
        return [(i[0].encode('hex'), i[1]) for i in self.get_chain(index)]

    def get_all_hex_chains(self):
        """Assemble and return chains for all nodes to the merkle root, in hex form
        """
        return [[(i[0].encode('hex'), i[1]) for i in j] for j in self.get_all_chains()]


def check_chain(chain):
    """Verify a presented merkle chain to see if the Merkle root can be reproduced.
    """
    link = chain[0][0]
    for i in range(1, len(chain) - 1):
        if chain[i][1] == 'R':
            link = hash_function(link + chain[i][0]).digest()
        elif chain[i][1] == 'L':
            link = hash_function(chain[i][0] + link).digest()
    if link == chain[-1][0]:
        return link
    else:
        raise AssertionError('The Merkle Chain is not valid')


def check_hex_chain(chain):
    """Verify a merkle chain, presented in hex form to see if the Merkle root can be reproduced.
    """
    return check_chain([(i[0].decode('hex'), i[1]) for i in chain]).encode('hex')

"""
from merkle import *
import json
q=MerkleTree()
for i in 'abcd':
    q.add(i)


# w=MerkleTree([i for i in 'abcd'])
q.build()
w.build()
q.root
w=q.leaves[2]
c=w.chain()
check_chain(c)
e=json.dumps(w.hex_chain())
check_hex_chain(json.loads(e))
"""
