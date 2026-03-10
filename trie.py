"""
Trie (Prefix Tree) implementation in Python.

Supports:
  - insert(word)       — add a word to the trie
  - search(word)       — check if a word exists in the trie
  - starts_with(prefix)— check if any word starts with the given prefix
  - delete(word)       — remove a word and clean up orphaned nodes
"""


class TrieNode:
    """A single node in the trie."""

    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False  # marks end of a valid word


class Trie:
    """
    Prefix tree with insert, search, starts_with, and delete.

    All operations are O(m) where m is the length of the word/prefix.
    Space complexity: O(n * m) where n is the number of words stored.
    """

    def __init__(self):
        self.root = TrieNode()

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, word: str) -> None:
        """Insert *word* into the trie.  Duplicate inserts are harmless."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, word: str) -> bool:
        """Return True if *word* is in the trie (full-word match)."""
        node = self._find_node(word)
        return node is not None and node.is_end

    # ------------------------------------------------------------------
    # Starts-with
    # ------------------------------------------------------------------

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word in the trie begins with *prefix*."""
        return self._find_node(prefix) is not None

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, word: str) -> bool:
        """
        Remove *word* from the trie.

        Returns True if the word existed and was deleted, False otherwise.
        Orphaned nodes (those that are no longer part of any word) are
        pruned as the recursion unwinds so we don't leak memory.
        """
        deleted = [False]  # use a list so the inner closure can mutate it

        def _delete(node: TrieNode, word: str, depth: int) -> bool:
            """
            Recursively delete *word* starting at *node* / *depth*.
            Returns True if *node* itself can be deleted (it has no other
            children and is not the end of another word).
            """
            if depth == len(word):
                if not node.is_end:
                    return False  # word doesn't exist
                node.is_end = False
                deleted[0] = True
                # Safe to delete this node if it has no children
                return len(node.children) == 0

            ch = word[depth]
            child = node.children.get(ch)
            if child is None:
                return False  # word doesn't exist

            should_delete_child = _delete(child, word, depth + 1)

            if should_delete_child:
                del node.children[ch]
                # Propagate deletion upward only if this node is also a leaf
                # (not the end of another word and has no remaining children)
                return not node.is_end and len(node.children) == 0

            return False

        _delete(self.root, word, 0)
        return deleted[0]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_node(self, prefix: str) -> "TrieNode | None":
        """Walk the trie following *prefix*; return the terminal node or None."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def __repr__(self) -> str:
        words = sorted(self._collect(self.root, ""))
        return f"Trie({words})"

    def _collect(self, node: TrieNode, prefix: str) -> list[str]:
        result = []
        if node.is_end:
            result.append(prefix)
        for ch, child in node.children.items():
            result.extend(self._collect(child, prefix + ch))
        return result
