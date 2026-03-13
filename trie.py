"""trie.py

A minimal Trie (prefix tree) implementation.

Public API:
- insert(word): insert a word
- search(word): exact-word membership
- starts_with(prefix): whether any inserted word has the given prefix
- delete(word): remove a word and clean up now-unneeded nodes

No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TrieNode:
    """Single node in a trie."""

    children: Dict[str, "TrieNode"] = field(default_factory=dict)
    is_end: bool = False


class Trie:
    """Trie data structure for efficient prefix operations."""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None

    def delete(self, word: str) -> bool:
        """Delete `word` if present.

        Returns:
            True if the word existed and was deleted; False otherwise.

        Deletion prunes nodes that become unreachable (no children, not end-of-word).
        """

        def _delete(node: TrieNode, i: int) -> bool:
            # Returns whether this node should be pruned from its parent.
            if i == len(word):
                if not node.is_end:
                    return False  # word not present
                node.is_end = False
                return len(node.children) == 0

            ch = word[i]
            child = node.children.get(ch)
            if child is None:
                return False  # word not present

            prune_child = _delete(child, i + 1)
            if prune_child:
                # Child subtree is now empty and not a word end.
                del node.children[ch]

            # Prune this node if it's now useless (except the root, which is never removed).
            return (node is not self.root) and (not node.is_end) and (len(node.children) == 0)

        # Special-case: empty word uses root's is_end marker.
        if word == "":
            if not self.root.is_end:
                return False
            self.root.is_end = False
            return True

        # We need a "found" signal independent of pruning; easiest is to check search first.
        if not self.search(word):
            return False

        _delete(self.root, 0)
        return True

    def _find_node(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            node = node.children.get(ch)  # type: ignore[assignment]
            if node is None:
                return None
        return node

    def __repr__(self) -> str:
        words: List[str] = []
        self._collect_words(self.root, "", words)
        return f"Trie({sorted(words)})"

    def _collect_words(self, node: TrieNode, prefix: str, out: List[str]) -> None:
        if node.is_end:
            out.append(prefix)
        for ch, child in node.children.items():
            self._collect_words(child, prefix + ch, out)
