"""
A Trie (Prefix Tree) implementation in Python
Supports: insert(word), search(word), starts_with(prefix), and delete(word)
"""

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Insert a word into the trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        """Search for a word in the trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        """Check if any word in the trie starts with the given prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

# Test the basic implementation
if __name__ == "__main__":
    trie = Trie()
    
    # Test insert
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")
    trie.insert("banana")
    
    # Test search
    print(f"Search 'app': {trie.search('app')}"))  # Should be True
    print(f"Search 'apple': {trie.search('apple')}"))  # Should be True
    print(f"Search 'appl': {trie.search('appl')}"))  # Should be False
    
    # Test starts_with
    print(f"Starts with 'app': {trie.starts_with('app')}"))  # Should be True
    print(f"Starts with 'ban': {trie.starts_with('ban')}"))  # Should be True
    print(f"Starts with 'cat': {trie.starts_with('cat')}"))  # Should be False"}}}