"""
Trie (Prefix Tree) Implementation

Supports:
- insert(word)
- search(word)
- starts_with(prefix)
- delete(word)
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
        """Return True if word exists in trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        """Return True if any word in trie starts with prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def delete(self, word):
        """Delete a word from the trie, cleaning up unused nodes"""
        def _delete_helper(node, word, index):
            if index == len(word):
                # We've reached the end of the word
                if not node.is_end_of_word:
                    return False  # Word not found
                node.is_end_of_word = False
                # Return True if this node has no children (can be deleted)
                return len(node.children) == 0
            
            char = word[index]
            if char not in node.children:
                return False  # Word not found
            
            should_delete_child = _delete_helper(node.children[char], word, index + 1)
            
            if should_delete_child:
                del node.children[char]
                
            # Return True if this node should be deleted (no longer end of word and no children)
            return not node.is_end_of_word and len(node.children) == 0
        
        return _delete_helper(self.root, word, 0)

# Test the implementation
if __name__ == "__main__":
    trie = Trie()
    
    # Test insert
    trie.insert("apple")
    trie.insert("app")
    trie.insert("application")
    trie.insert("appreciate")
    
    # Test search
    print(f"Search 'app': {trie.search('app')}"))
    print(f"Search 'apple': {trie.search('apple')}"))
    print(f"Search 'appl': {trie.search('appl')}"))
    
    # Test starts_with
    print(f"Starts with 'app': {trie.starts_with('app')}"))
    print(f"Starts with 'appl': {trie.starts_with('appl')}"))
    print(f"Starts with 'banana': {trie.starts_with('banana')}"))
    
    # Test delete
    trie.delete("app")
    print(f"After deleting 'app', search 'app': {trie.search('app')}"))
    print(f"After deleting 'app', starts with 'app': {trie.starts_with('app')}"))
    
    # Test delete with shared prefix
    trie.delete("apple")
    print(f"After deleting 'apple', search 'app': {trie.search('app')}"))
    print(f"After deleting 'apple', starts with 'app': {trie.starts_with('app')}"))
    
    # Test delete non-existent word
    result = trie.delete("banana")
    print(f"Delete non-existent 'banana': {result}")
"""