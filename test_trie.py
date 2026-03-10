"""
Tests for trie.py
"""
import pytest
from trie import Trie


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_trie(*words: str) -> Trie:
    t = Trie()
    for w in words:
        t.insert(w)
    return t


# ---------------------------------------------------------------------------
# insert / search
# ---------------------------------------------------------------------------

class TestInsertSearch:
    def test_search_inserted_word(self):
        t = make_trie("apple")
        assert t.search("apple") is True

    def test_search_missing_word(self):
        t = make_trie("apple")
        assert t.search("app") is False

    def test_search_prefix_only(self):
        t = make_trie("apple")
        assert t.search("appl") is False

    def test_search_empty_string(self):
        t = Trie()
        assert t.search("") is False
        t.insert("")
        assert t.search("") is True

    def test_duplicate_insert(self):
        t = Trie()
        t.insert("cat")
        t.insert("cat")
        assert t.search("cat") is True

    def test_multiple_words(self):
        words = ["bat", "ball", "batman", "band", "can"]
        t = make_trie(*words)
        for w in words:
            assert t.search(w) is True
        assert t.search("ba") is False
        assert t.search("bats") is False


# ---------------------------------------------------------------------------
# starts_with
# ---------------------------------------------------------------------------

class TestStartsWith:
    def test_prefix_exists(self):
        t = make_trie("apple", "app", "application")
        assert t.starts_with("app") is True
        assert t.starts_with("appl") is True
        assert t.starts_with("a") is True

    def test_prefix_not_exists(self):
        t = make_trie("apple")
        assert t.starts_with("b") is False
        assert t.starts_with("apples") is False

    def test_full_word_is_prefix(self):
        t = make_trie("apple")
        assert t.starts_with("apple") is True  # exact word counts

    def test_empty_prefix(self):
        t = make_trie("anything")
        assert t.starts_with("") is True  # root always exists

    def test_empty_trie(self):
        t = Trie()
        assert t.starts_with("a") is False


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_existing_word(self):
        t = make_trie("apple")
        assert t.delete("apple") is True
        assert t.search("apple") is False

    def test_delete_returns_false_for_missing_word(self):
        t = make_trie("apple")
        assert t.delete("app") is False
        assert t.delete("banana") is False

    def test_delete_does_not_affect_prefix(self):
        t = make_trie("apple", "app")
        t.delete("apple")
        assert t.search("app") is True   # prefix-word still present
        assert t.search("apple") is False

    def test_delete_does_not_affect_extension(self):
        t = make_trie("app", "apple")
        t.delete("app")
        assert t.search("app") is False
        assert t.search("apple") is True  # longer word untouched

    def test_delete_cleans_up_orphaned_nodes(self):
        """After deleting a unique word, its nodes should be pruned."""
        t = make_trie("xyz")
        assert "x" in t.root.children
        t.delete("xyz")
        assert "x" not in t.root.children  # node was cleaned up

    def test_delete_keeps_shared_prefix_nodes(self):
        """Shared prefix nodes must NOT be removed when only one word is deleted."""
        t = make_trie("bat", "ball")
        t.delete("bat")
        # 'b' and 'a' are shared — they must still exist for 'ball'
        assert t.starts_with("ba") is True
        assert t.search("ball") is True
        assert t.search("bat") is False

    def test_delete_empty_string(self):
        t = Trie()
        t.insert("")
        assert t.delete("") is True
        assert t.search("") is False

    def test_delete_all_words(self):
        words = ["can", "cat", "car", "card"]
        t = make_trie(*words)
        for w in words:
            assert t.delete(w) is True
        for w in words:
            assert t.search(w) is False
        # Trie should be essentially empty
        assert t.root.children == {}

    def test_double_delete(self):
        t = make_trie("hello")
        assert t.delete("hello") is True
        assert t.delete("hello") is False  # already gone

    def test_delete_one_of_many(self):
        words = ["test", "testing", "tester", "tested"]
        t = make_trie(*words)
        t.delete("testing")
        assert t.search("testing") is False
        for w in ["test", "tester", "tested"]:
            assert t.search(w) is True


# ---------------------------------------------------------------------------
# Repr / collect sanity
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr_lists_all_words(self):
        words = ["fig", "fire", "fit"]
        t = make_trie(*words)
        assert repr(t) == f"Trie({sorted(words)})"

    def test_repr_empty(self):
        t = Trie()
        assert repr(t) == "Trie([])"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
