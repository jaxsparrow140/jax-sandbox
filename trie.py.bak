"""
Trie (Prefix Tree) implementation in Python — stdlib only.

Public API
----------
insert(word)        — add a word to the trie
search(word)        — True iff the exact word is stored
starts_with(prefix) — True iff any stored word begins with prefix
delete(word)        — remove word and prune orphaned nodes; returns bool
"""

from typing import Dict, List, Optional, Tuple


class TrieNode:
    __slots__ = ("children", "is_end_of_word")

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False


class Trie:
    """
    Trie backed by a dictionary of children at each node.

    Time complexity (n = word length):
        insert / search / starts_with / delete — O(n)
    Space complexity: O(total characters across all stored words)
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    # ------------------------------------------------------------------ #
    # Core operations                                                       #
    # ------------------------------------------------------------------ #

    def insert(self, word: str) -> None:
        """Insert *word* into the trie (idempotent)."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """Return True iff *word* is stored (exact match, not prefix)."""
        node = self._find_node(word)
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """Return True iff at least one stored word starts with *prefix*.

        The empty prefix matches any non-empty trie (and an empty trie if
        ``insert("")`` was called).
        """
        return self._find_node(prefix) is not None

    def delete(self, word: str) -> bool:
        """Remove *word* and prune now-orphaned nodes.

        Algorithm
        ---------
        1. Walk down the trie, recording the path of (parent, char) pairs.
        2. If the word is absent (missing node or terminal flag not set),
           return False immediately — the trie is unmodified.
        3. Clear the terminal flag on the leaf.
        4. Walk *back up* the recorded path: delete a child node only when
           it has no remaining children and is not itself a word-end (i.e.
           it is now a dead-end with no purpose).  Stop as soon as we hit
           a node that must be kept.

        Returns True if the word existed and was removed, False otherwise.
        """
        # path[i] = (parent_node, char_to_reach_child)
        path: List[Tuple[TrieNode, str]] = []
        node = self.root

        for ch in word:
            if ch not in node.children:
                return False  # word not present
            path.append((node, ch))
            node = node.children[ch]

        if not node.is_end_of_word:
            return False  # prefix exists but not a complete word

        node.is_end_of_word = False

        # Prune upward: remove dead-end nodes only.
        for parent, ch in reversed(path):
            child = parent.children[ch]
            if child.is_end_of_word or child.children:
                break  # child still needed — stop here
            del parent.children[ch]

        return True

    # ------------------------------------------------------------------ #
    # Internals & dunder helpers                                            #
    # ------------------------------------------------------------------ #

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Return the node at the end of *prefix*, or None if not reachable."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect_words(self) -> list[str]:
        """DFS traversal — returns all stored words in sorted order."""
        words: List[str] = []

        def dfs(node: TrieNode, buf: list[str]) -> None:
            if node.is_end_of_word:
                words.append("".join(buf))
            for ch, child in node.children.items():
                buf.append(ch)
                dfs(child, buf)
                buf.pop()

        dfs(self.root, [])
        words.sort()
        return words

    def __repr__(self) -> str:
        return f"Trie({self._collect_words()})"


# ------------------------------------------------------------------ #
# Quick smoke test                                                      #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    t = Trie()

    for w in ("apple", "app", "application", "banana"):
        t.insert(w)

    print("=== search ===")
    print(f"  'app'         → {t.search('app')}")          # True
    print(f"  'apple'       → {t.search('apple')}")        # True
    print(f"  'appl'        → {t.search('appl')}")         # False
    print(f"  'apply'       → {t.search('apply')}")        # False

    print("\n=== starts_with ===")
    print(f"  'app'         → {t.starts_with('app')}")     # True
    print(f"  'ban'         → {t.starts_with('ban')}")     # True
    print(f"  'cat'         → {t.starts_with('cat')}")     # False
    print(f"  ''            → {t.starts_with('')}")        # True (empty prefix)

    print("\n=== delete ===")
    print(f"  delete 'apple'  → {t.delete('apple')}")      # True
    print(f"  search 'apple'  → {t.search('apple')}")      # False
    print(f"  search 'app'    → {t.search('app')}")        # True (not pruned)
    print(f"  delete 'ghost'  → {t.delete('ghost')}")      # False (never inserted)

    print(f"\n=== repr ===\n  {t!r}")
