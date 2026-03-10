"""Trie (prefix tree) with insert, search, starts_with, and delete."""

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
        """Delete a word from the trie, pruning orphaned nodes.

        Returns True if the word was found and removed, False otherwise.
        """
        return self._delete(self.root, word, 0)

    # ── internals ────────────────────────────────────────────────────

    def _find(self, prefix: str) -> Optional[TrieNode]:
        """Walk the trie along `prefix`; return the landing node or None."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _delete(self, node: TrieNode, word: str, depth: int) -> bool:
        """Recursively delete `word` starting at `depth`.

        Post-order traversal: after the recursive call returns, each frame
        checks whether its child node is now a childless non-endpoint and
        prunes it if so.  Returns True when the word was actually removed.
        """
        if depth == len(word):
            if not node.is_end:
                return False          # word not in trie
            node.is_end = False
            return True

        ch = word[depth]
        child = node.children.get(ch)
        if child is None:
            return False              # word not in trie

        found = self._delete(child, word, depth + 1)

        # prune the child if it's now empty and not a word endpoint
        if found and not child.is_end and not child.children:
            del node.children[ch]

        return found


# ── quick smoke test ─────────────────────────────────────────────────

if __name__ == "__main__":
    t = Trie()

    # insert a few words
    for w in ("apple", "app", "application", "bat", "ball"):
        t.insert(w)

    # search
    assert t.search("apple")
    assert t.search("app")
    assert not t.search("ap")
    assert t.search("bat")
    assert not t.search("batman")

    # prefix
    assert t.starts_with("app")
    assert t.starts_with("ba")
    assert not t.starts_with("cat")

    # delete leaf – "application" shares prefix with "apple"/"app"
    assert t.delete("application")
    assert not t.search("application")
    assert t.search("apple")           # sibling intact
    assert t.search("app")             # shorter word intact

    # delete shorter word – "app" should go, "apple" stays
    assert t.delete("app")
    assert not t.search("app")
    assert t.search("apple")
    assert t.starts_with("app")        # prefix still valid via "apple"

    # delete remaining word sharing a prefix
    assert t.delete("apple")
    assert not t.search("apple")
    assert not t.starts_with("app")    # entire branch pruned

    # double-delete returns False
    assert not t.delete("apple")

    # unrelated words untouched
    assert t.search("bat")
    assert t.search("ball")

    # delete everything
    assert t.delete("bat")
    assert t.delete("ball")
    assert not t.starts_with("b")

    print("All tests passed ✓")
