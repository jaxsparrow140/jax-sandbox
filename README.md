# Trie (Prefix Tree) Implementation

A Python implementation of a trie (prefix tree) data structure that supports:

- `insert(word)`: Insert a word into the trie
- `search(word)`: Search for a complete word in the trie
- `starts_with(prefix)`: Check if any word in the trie starts with the given prefix
- `delete(word)`: Delete a word from the trie and clean up unused nodes

## Usage

```python
from trie import Trie

trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("application")

print(trie.search("app"))        # True
print(trie.search("apple"))      # True
print(trie.search("appl"))       # False
print(trie.starts_with("app"))   # True
print(trie.starts_with("cat"))   # False

trie.delete("app")
print(trie.search("app"))        # False
print(trie.starts_with("app"))   # True (because 'apple' and 'application' still exist)
```

## Implementation Details

- Uses a recursive helper function for deletion to properly clean up nodes
- Each node contains a dictionary of children and a boolean flag indicating if it's the end of a word
- Deletion removes nodes only when they are no longer needed (no children and not end of word)
- No external dependencies

## Testing

The implementation includes comprehensive test cases that verify:
- Correct insertion of words
- Accurate search for complete words
- Proper prefix matching with starts_with
- Correct deletion with cleanup of unused nodes

Run tests with: `python3 trie.py`

## License

MIT
