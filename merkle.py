from hashlib import sha256


class Node(object):
    """Each node can have it's own references to left and right child nodes, it's parent, and sibling.
    It can also be aware of whether it is on the left or right hand side.
    """
    def __init__(self, data):
        self.l = None
        self.r = None
        self.val = sha256(data).digest()
        self.p = None
        self.sib = None
        self.side = None

    def __repr__(self):
        return "Val: <" + str(self.val.encode('hex')) + ">"

    def chain(self):
        """Assemble and return the chain leading to the merkle root of this tree
        """
        chain = []
        this = self
        chain.append((this.val, "SELF"))
        while 1:
            if not this.p:
                chain.append((this.val, "ROOT"))
                break
            else:
                chain.append((this.sib.val, this.sib.side))
                this = this.p
        return chain


class MerkleTree(object):
    """A Merkle tree implemntation.  Added values are stored in a list until the tree is built.
    """
    def __init__(self):
        self.leaves = []
        self.root = None

    def add(self, data):
        """Add a value to the tree, it's value is hashed automatically
        """
        self.leaves.append(Node(data))
        # if self.root:
        #     self.calc()

    def add_hash(self, _hash):
        """Add a precomputed hash value
        """
        new_node = Node('temp')
        new_node.val = _hash.decode('hex')
        self.leaves.append(new_node)

    def clear(self):
        """releases the Merkle root, and node references are garbage collected
        """
        self.root = None

    def calc(self):
        """calculate the merkle root and make references in the whole tree.
        """
        layer = self.leaves[::]
        while 1:
            layer = self._build(layer)
            if len(layer) == 1:
                self.root = layer[0]
                break

    def _build(self, leaves):
        """private helper function to create the next aggregation level and put all references in place
        """
        new = []
        # ensure even number of leaves
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        for i in range(0, len(leaves), 2):
            newnode = Node(leaves[i].val + leaves[i + 1].val)
            newnode.l, newnode.r = leaves[i], leaves[i + 1]
            leaves[i].side, leaves[i + 1].side, leaves[i].p, leaves[i + 1].p = 'L', 'R', newnode, newnode
            leaves[i].sib, leaves[i + 1].sib = leaves[i + 1], leaves[i]
            new.append(newnode)
        return new

    def combine(self, l_node, r_node):
        return sha256(l_node.val + r_node.val).digest()


def check_chain(chain):
    """verify a presented merkle chain
    """
    link = chain[0][0]
    for i in range(1, len(chain) - 1):
        if chain[i][1] == 'R':
            link = sha256(link + chain[i][0]).digest()
        elif chain[i][1] == 'L':
            link = sha256(chain[i][0] + link).digest()
    if link == chain[-1][0]:
        print 'success', link.encode('hex')
    else:
        print 'failure', link.encode('hex')

"""
from merkle import Node, MerkleTree, check_chain
q=MerkleTree()
for i in 'abcd':
    q.add(i)


q.calc()
q.root
w=q.leaves[2]
c=w.chain()
check_chain(c)
"""