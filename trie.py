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
        """Delete a word from the trie and clean up unused nodes"""
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
    print("Deleting 'app'")
    trie.delete("app")
    print("Searching for 'app':", trie.search("app"))  # False
    print("Starts with 'app':", trie.starts_with("app"))  # True (because 'apple' and 'application' still exist)
    print("Searching for 'apple':", trie.search("apple"))  # True
    
    # Test delete 'apple'
    print("Deleting 'apple'")
    trie.delete("apple")
    print("Searching for 'apple':", trie.search("apple"))  # False
    print("Starts with 'app':", trie.starts_with("app"))  # True (because 'application' still exists)
    print("Searching for 'application':", trie.search("application"))  # True
    
    # Test delete 'application'
    print("Deleting 'application'")
    trie.delete("application")
    print("Searching for 'application':", trie.search("application"))  # False
    print("Starts with 'app':", trie.starts_with("app"))  # False (no words left starting with 'app')
    
    # Test delete 'banana'
    print("Deleting 'banana'")
    trie.delete("banana")
    print("Searching for 'banana':", trie.search("banana"))  # False
    print("Starts with 'ban':", trie.starts_with("ban"))  # True (because 'band' and 'bandana' still exist)
    
    # Test delete 'band'
    print("Deleting 'band'")
    trie.delete("band")
    print("Searching for 'band':", trie.search("band"))  # False
    print("Starts with 'ban':", trie.starts_with("ban"))  # True (because 'bandana' still exists)
    
    # Test delete 'bandana'
    print("Deleting 'bandana'")
    trie.delete("bandana")
    print("Searching for 'bandana':", trie.search("bandana"))  # False
    print("Starts with 'ban':", trie.starts_with("ban"))  # False (no words left starting with 'ban')
    
    print("All tests completed.")

