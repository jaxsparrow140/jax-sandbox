"""Tests for trie.py (standard-library only)."""

import unittest

from trie import Trie


def make_trie(*words: str) -> Trie:
    t = Trie()
    for w in words:
        t.insert(w)
    return t


class TestInsertSearch(unittest.TestCase):
    def test_search_inserted_word(self):
        t = make_trie("apple")
        self.assertTrue(t.search("apple"))

    def test_search_missing_word(self):
        t = make_trie("apple")
        self.assertFalse(t.search("app"))

    def test_search_prefix_only(self):
        t = make_trie("apple")
        self.assertFalse(t.search("appl"))

    def test_search_empty_string(self):
        t = Trie()
        self.assertFalse(t.search(""))
        t.insert("")
        self.assertTrue(t.search(""))

    def test_duplicate_insert(self):
        t = Trie()
        t.insert("cat")
        t.insert("cat")
        self.assertTrue(t.search("cat"))

    def test_multiple_words(self):
        words = ["bat", "ball", "batman", "band", "can"]
        t = make_trie(*words)
        for w in words:
            self.assertTrue(t.search(w))
        self.assertFalse(t.search("ba"))
        self.assertFalse(t.search("bats"))


class TestStartsWith(unittest.TestCase):
    def test_prefix_exists(self):
        t = make_trie("apple", "app", "application")
        self.assertTrue(t.starts_with("app"))
        self.assertTrue(t.starts_with("appl"))
        self.assertTrue(t.starts_with("a"))

    def test_prefix_not_exists(self):
        t = make_trie("apple")
        self.assertFalse(t.starts_with("b"))
        self.assertFalse(t.starts_with("apples"))

    def test_full_word_is_prefix(self):
        t = make_trie("apple")
        self.assertTrue(t.starts_with("apple"))

    def test_empty_prefix(self):
        t = make_trie("anything")
        self.assertTrue(t.starts_with(""))

    def test_empty_trie(self):
        t = Trie()
        self.assertFalse(t.starts_with("a"))


class TestDelete(unittest.TestCase):
    def test_delete_existing_word(self):
        t = make_trie("apple")
        self.assertTrue(t.delete("apple"))
        self.assertFalse(t.search("apple"))

    def test_delete_returns_false_for_missing_word(self):
        t = make_trie("apple")
        self.assertFalse(t.delete("app"))
        self.assertFalse(t.delete("banana"))

    def test_delete_does_not_affect_prefix(self):
        t = make_trie("apple", "app")
        self.assertTrue(t.delete("apple"))
        self.assertTrue(t.search("app"))
        self.assertFalse(t.search("apple"))

    def test_delete_does_not_affect_extension(self):
        t = make_trie("app", "apple")
        self.assertTrue(t.delete("app"))
        self.assertFalse(t.search("app"))
        self.assertTrue(t.search("apple"))

    def test_delete_cleans_up_orphaned_nodes(self):
        t = make_trie("xyz")
        self.assertIn("x", t.root.children)
        self.assertTrue(t.delete("xyz"))
        self.assertNotIn("x", t.root.children)

    def test_delete_keeps_shared_prefix_nodes(self):
        t = make_trie("bat", "ball")
        self.assertTrue(t.delete("bat"))
        self.assertTrue(t.starts_with("ba"))
        self.assertTrue(t.search("ball"))
        self.assertFalse(t.search("bat"))

    def test_delete_empty_string(self):
        t = Trie()
        t.insert("")
        self.assertTrue(t.delete(""))
        self.assertFalse(t.search(""))

    def test_delete_all_words(self):
        words = ["can", "cat", "car", "card"]
        t = make_trie(*words)
        for w in words:
            self.assertTrue(t.delete(w))
        for w in words:
            self.assertFalse(t.search(w))
        self.assertEqual(t.root.children, {})

    def test_double_delete(self):
        t = make_trie("hello")
        self.assertTrue(t.delete("hello"))
        self.assertFalse(t.delete("hello"))

    def test_delete_one_of_many(self):
        words = ["test", "testing", "tester", "tested"]
        t = make_trie(*words)
        self.assertTrue(t.delete("testing"))
        self.assertFalse(t.search("testing"))
        for w in ["test", "tester", "tested"]:
            self.assertTrue(t.search(w))


class TestRepr(unittest.TestCase):
    def test_repr_lists_all_words(self):
        words = ["fig", "fire", "fit"]
        t = make_trie(*words)
        self.assertEqual(repr(t), f"Trie({sorted(words)})")

    def test_repr_empty(self):
        t = Trie()
        self.assertEqual(repr(t), "Trie([])")


if __name__ == "__main__":
    unittest.main()
