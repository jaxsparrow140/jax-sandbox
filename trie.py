"""
Trie (Prefix Tree) Implementation

Supports:
- insert(word): Insert a word into the trie
- search(word): Check if a word exists in the trie
- starts_with(prefix): Check if any word starts with the given prefix
- delete(word): Remove a word and clean up unnecessary nodes
"""


class TrieNode:
    """A node in the trie."""
    
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end = False  # Marks end of a word


class Trie:
    """Trie data structure for efficient prefix operations."""
    
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word: str) -> bool:
        """Check if a word exists in the trie."""
        node = self._find_node(word)
        return node is not None and node.is_end
    
    def starts_with(self, prefix: str) -> bool:
        """Check if any word in the trie starts with the given prefix."""
        node = self._find_node(prefix)
        return node is not None
    
    def _find_node(self, s: str) -> TrieNode | None:
        """Navigate to the node corresponding to string s."""
        node = self.root
        for char in s:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def delete(self, word: str) -> bool:
        """
        Delete a word from the trie.
        Returns True if the word was found and deleted, False otherwise.
        Properly cleans up nodes that are no longer needed.
        """
        if not word:
            return False
        
        # Track the path for potential cleanup
        path = []  # List of (node, char) tuples
        node = self.root
        
        # Navigate through the word
        for char in word:
            if char not in node.children:
                return False  # Word doesn't exist
            path.append((node, char))
            node = node.children[char]
        
        # Check if this is actually a word
        if not node.is_end:
            return False
        
        # Mark as not a word anymore
        node.is_end = False
        
        # Clean up nodes that are no longer needed
        # A node can be removed if:
        # 1. It's not an end of another word
        # 2. It has no children
        # Walk back from the end of the word
        for parent, char in reversed(path):
            child = parent.children[char]
            if not child.is_end and not child.children:
                # Safe to remove this child
                del parent.children[char]
            else:
                # Can't remove further up - this node is still needed
                break
        
        return True
    
    def __repr__(self) -> str:
        """Return a string representation of the trie."""
        words = []
        self._collect_words(self.root, "", words)
        return f"Trie({len(words)} words: {words})"
    
    def _collect_words(self, node: TrieNode, prefix: str, words: list) -> None:
        """Collect all words from the trie."""
        if node.is_end:
            words.append(prefix)
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, words)


def test_trie():
    """Test the trie implementation."""
    trie = Trie()
    
    # Test insert and search
    print("Testing insert and search...")
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")
    trie.insert("banana")
    
    assert trie.search("apple") == True
    assert trie.search("app") == True
    assert trie.search("application") == True
    assert trie.search("banana") == True
    assert trie.search("appl") == False
    assert trie.search("ban") == False
    print("✓ Insert and search work correctly")
    
    # Test starts_with
    print("Testing starts_with...")
    assert trie.starts_with("app") == True
    assert trie.starts_with("appl") == True
    assert trie.starts_with("ban") == True
    assert trie.starts_with("xyz") == False
    print("✓ starts_with works correctly")
    
    # Test delete
    print("Testing delete...")
    
    # Delete "app" - should work
    assert trie.delete("app") == True
    assert trie.search("app") == False
    assert trie.search("apple") == True  # "apple" should still exist
    assert trie.starts_with("app") == True  # "apple" and "application" still have "app" prefix
    
    # Delete "apple"
    assert trie.delete("apple") == True
    assert trie.search("apple") == False
    assert trie.search("application") == True
    
    # Delete "application"
    assert trie.delete("application") == True
    assert trie.search("application") == False
    assert trie.starts_with("app") == False  # No more words with "app" prefix
    
    # Delete non-existent word
    assert trie.delete("app") == False
    
    # Delete "banana"
    assert trie.delete("banana") == True
    assert trie.search("banana") == False
    
    print("✓ Delete works correctly")
    
    # Test edge cases
    print("Testing edge cases...")
    
    # Empty trie
    empty_trie = Trie()
    assert empty_trie.search("anything") == False
    assert empty_trie.delete("anything") == False
    assert empty_trie.starts_with("anything") == False
    
    # Single character words
    trie.insert("a")
    trie.insert("ab")
    assert trie.search("a") == True
    assert trie.delete("a") == True
    assert trie.search("a") == False
    assert trie.search("ab") == True  # "ab" should still exist
    
    print("✓ Edge cases handled correctly")
    
    print("\nAll tests passed! ✅")


if __name__ == "__main__":
    test_trie()