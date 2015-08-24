# merkletree
A Python implementation of the Merkle Hash Tree Algorithm using sha256

This implementation uses distinct node objects which are designed to be easily traversible.  Each node has references to it's children, parent, and sibling nodes.  The node also has a convenience method for accessing the root from it to the Merkle root.

2015