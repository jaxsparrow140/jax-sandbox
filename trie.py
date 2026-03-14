"""
Trie (Prefix Tree) Implementation
Supports: insert(word), search(word), starts_with(prefix), delete(word)
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
        """Search for a complete word in the trie"""
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
                # Return True if this node is not an end of word and has no children
                return not node.is_end_of_word and len(node.children) == 0
            
            return False
        
        _delete_helper(self.root, word, 0)

# Test function
if __name__ == "__main__":
    trie = Trie()
    
    # Test insert
    words = ["apple", "app", "application", "appreciate", "banana", "band", "bandana"]
    for word in words:
        trie.insert(word)
    
    # Test search
    print("Searching for 'app':", trie.search("app"))  # True
    print("Searching for 'apple':", trie.search("apple"))  # True
    print("Searching for 'appl':", trie.search("appl"))  # False
    
    # Test starts_with
    print("Starts with 'app':", trie.starts_with("app"))  # True
    print("Starts with 'ban':", trie.starts_with("ban"))  # True
    print("Starts with 'cat':", trie.starts_with("cat"))  # False
    
    # Test delete
    trie.delete("app")
    print("After deleting 'app':")
    print("Searching for 'app':", trie.search("app"))  # False
    print("Searching for 'apple':", trie.search("apple"))  # True
    print("Starts with 'app':", trie.starts_with("app"))  # True (because 'application' and 'appreciate' still exist)
    
    trie.delete("apple")
    print("After deleting 'apple':")
    print("Searching for 'apple':", trie.search("apple"))  # False
    print("Starts with 'app':", trie.starts_with("app"))  # True (because 'application' and 'appreciate' still exist)
    
    # Verify remaining words starting with 'app'
    print("Remaining words starting with 'app':")
    for word in ["application", "appreciate"]:
        print(f"  {word}: {trie.search(word)}")
    
    trie.delete("nonexistent")
    print("Deleted nonexistent word - no error")
    
    trie.insert("")
    print("Inserted empty string")
    print("Search empty string:", trie.search(""))  # True
    trie.delete("")
    print("Deleted empty string")
    print("Search empty string:", trie.search(""))  # False
