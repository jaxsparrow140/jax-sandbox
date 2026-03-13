"""
Trie (Prefix Tree) implementation with insert, search, starts_with, and delete.
No external libraries.
"""
from __future__ import annotations

from typing import Dict, Optional


class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end: bool = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    # ── core operations ──────────────────────────────────────────────

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        """Return True if the exact word exists in the trie."""
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word in the trie starts with the given prefix."""
        return self._find(prefix) is not None

    def delete(self, word: str) -> bool:
        """
        Delete a word from the trie.  Cleans up nodes that are no longer
        part of any other word.  Returns True if the word was found and
        removed, False otherwise.
        """
        found, _ = self._delete(self.root, word, 0)
        return found

    # ── internals ────────────────────────────────────────────────────

    def _find(self, prefix: str) -> Optional[TrieNode]:
        """Walk the trie following `prefix`; return the landing node or None."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _delete(self, node: TrieNode, word: str, depth: int) -> tuple:
        """
        Recursively delete `word` starting at `depth`.

        Returns (found, should_prune):
          found       – True if the word existed and was removed
          should_prune – True when the parent should drop this child node
        """
        if depth == len(word):
            if not node.is_end:
                return False, False        # word doesn't exist
            node.is_end = False            # un-mark end
            return True, len(node.children) == 0

        ch = word[depth]
        child = node.children.get(ch)
        if child is None:
            return False, False            # word doesn't exist

        found, should_prune = self._delete(child, word, depth + 1)

        if should_prune:
            del node.children[ch]
            # Propagate prune if this node is now a childless non-terminal
            return found, not node.is_end and len(node.children) == 0

        return found, False


# ── tests ────────────────────────────────────────────────────────────

def _run_tests():
    t = Trie()

    # basic insert / search / starts_with
    t.insert("apple")
    assert t.search("apple") is True
    assert t.search("app") is False
    assert t.starts_with("app") is True
    assert t.starts_with("apl") is False

    t.insert("app")
    assert t.search("app") is True

    # delete leaf word — should not break prefix
    assert t.delete("apple") is True
    assert t.search("apple") is False
    assert t.search("app") is True       # "app" still there

    # delete remaining word
    assert t.delete("app") is True
    assert t.search("app") is False
    assert t.starts_with("a") is False    # trie fully cleaned up

    # delete non-existent word
    assert t.delete("ghost") is False

    # delete prefix word — should not break longer word
    t.insert("banana")
    t.insert("ban")
    assert t.delete("ban") is True
    assert t.search("ban") is False
    assert t.search("banana") is True     # longer word intact

    # delete longer word — should clean up suffix nodes
    assert t.delete("banana") is True
    assert t.starts_with("b") is False    # all cleaned up

    # bulk insert then selective delete
    words = ["car", "card", "care", "cared", "cars"]
    for w in words:
        t.insert(w)
    assert t.delete("cared") is True
    assert t.search("care") is True
    assert t.search("cared") is False
    assert t.delete("cars") is True
    assert t.search("car") is True
    assert t.starts_with("cars") is False
    assert t.starts_with("car") is True

    # empty-string edge case
    t2 = Trie()
    t2.insert("")
    assert t2.search("") is True
    t2.delete("")
    assert t2.search("") is False

    print("All tests passed.")


if __name__ == "__main__":
    _run_tests()
