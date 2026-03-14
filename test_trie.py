"""
Test suite for the Trie implementation.
"""

import unittest
from trie import Trie

class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
    
    def test_insert_and_search(self):
        # Insert some words
        self.trie.insert("apple")
        self.trie.insert("app")
        self.trie.insert("application")
        
        # Test search
        self.assertTrue(self.trie.search("apple"))
        self.assertTrue(self.trie.search("app"))
        self.assertTrue(self.trie.search("application"))
        self.assertFalse(self.trie.search("appl"))
        self.assertFalse(self.trie.search("banana"))
    
    def test_starts_with(self):
        # Insert some words
        self.trie.insert("apple")
        self.trie.insert("app")
        self.trie.insert("application")
        self.trie.insert("banana")
        
        # Test starts_with
        self.assertTrue(self.trie.starts_with("app"))
        self.assertTrue(self.trie.starts_with("appl"))
        self.assertTrue(self.trie.starts_with("a"))
        self.assertFalse(self.trie.starts_with("banan"))
        self.assertFalse(self.trie.starts_with("xyz"))
    
    def test_delete(self):
        # Insert some words
        self.trie.insert("apple")
        self.trie.insert("app")
        self.trie.insert("application")
        self.trie.insert("apples")
        
        # Test delete
        self.trie.delete("app")
        self.assertFalse(self.trie.search("app"))
        self.assertTrue(self.trie.search("apple"))
        self.assertTrue(self.trie.search("application"))
        self.assertTrue(self.trie.search("apples"))
        
        # Delete a word that's a prefix of another
        self.trie.delete("apple")
        self.assertFalse(self.trie.search("apple"))
        self.assertTrue(self.trie.search("apples"))
        
        # Delete the last remaining word
        self.trie.delete("apples")
        self.assertFalse(self.trie.search("apples"))
        self.assertTrue(self.trie.search("application"))
        
        # Delete the last word
        self.trie.delete("application")
        self.assertFalse(self.trie.search("application"))
        
        # Verify trie is empty
        self.assertFalse(self.trie.starts_with("a"))
        
    def test_delete_nonexistent(self):
        # Insert some words
        self.trie.insert("apple")
        self.trie.insert("app")
        
        # Try to delete a word that doesn't exist
        self.trie.delete("banana")
        self.assertTrue(self.trie.search("apple"))
        self.assertTrue(self.trie.search("app"))
        
    def test_delete_with_overlap(self):
        # Insert overlapping words
        self.trie.insert("cat")
        self.trie.insert("caterpillar")
        
        # Delete "cat" - should not affect "caterpillar"
        self.trie.delete("cat")
        self.assertFalse(self.trie.search("cat"))
        self.assertTrue(self.trie.search("caterpillar"))
        self.assertTrue(self.trie.starts_with("cate"))
        
if __name__ == '__main__':
    unittest.main()