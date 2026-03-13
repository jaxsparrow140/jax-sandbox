"""
LRU Cache Implementation from Scratch

O(1) get(key) and put(key, value) using:
- Hash map (dict) for O(1) key lookup
- Doubly linked list for O(1) insertion/deletion

When capacity is exceeded, the least recently used item is evicted.
"""


class Node:
    """Doubly linked list node."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """LRU Cache with O(1) get and put operations."""
    
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.size = 0
        
        # Hash map: key -> Node
        self.cache: dict = {}
        
        # Doubly linked list with dummy head/tail for O(1) operations
        self.head = Node(None, None)  # dummy head (most recent)
        self.tail = Node(None, None)  # dummy tail (least recent)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node: Node):
        """Add node right after head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: Node):
        """Remove a node from the linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _evict_lru(self):
        """Remove the least recently used item (right before tail)."""
        lru_node = self.tail.prev
        
        # Remove from linked list
        self._remove_node(lru_node)
        
        # Remove from hash map
        del self.cache[lru_node.key]
        
        self.size -= 1
    
    def get(self, key):
        """
        Get value for key. Returns None if key doesn't exist.
        Moves accessed node to head (most recently used).
        Time: O(1)
        """
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        
        # Move to head (mark as most recently used)
        self._remove_node(node)
        self._add_to_head(node)
        
        return node.value
    
    def put(self, key, value):
        """
        Insert or update key-value pair.
        If capacity exceeded, evicts least recently used item.
        Time: O(1)
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            
            # Move to head (most recently used)
            self._remove_node(node)
            self._add_to_head(node)
        else:
            # New key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            self.size += 1
            
            # Evict if over capacity
            if self.size > self.capacity:
                self._evict_lru()


def test_lru_cache():
    """Test the LRU cache implementation."""
    
    print("=== LRU Cache Tests ===\n")
    
    # Test 1: Basic put/get
    print("Test 1: Basic put/get")
    cache = LRUCache(2)
    cache.put(1, "a")
    cache.put(2, "b")
    
    assert cache.get(1) == "a", "Failed: get(1) should return 'a'"
    assert cache.get(2) == "b", "Failed: get(2) should return 'b'"
    print("✓ Basic put/get works")
    
    # Test 2: LRU eviction
    print("\nTest 2: LRU eviction")
    cache.put(3, "c")  # Should evict key 1 (least recently used)
    
    assert cache.get(1) is None, "Failed: key 1 should be evicted"
    assert cache.get(2) == "b", "Failed: key 2 should still exist"
    assert cache.get(3) == "c", "Failed: key 3 should exist"
    print("✓ LRU eviction works")
    
    # Test 3: Update existing key
    print("\nTest 3: Update existing key")
    cache.put(2, "b_updated")
    assert cache.get(2) == "b_updated", "Failed: update should work"
    print("✓ Update existing key works")
    
    # Test 4: Access changes LRU order
    print("\nTest 4: Access changes LRU order")
    cache2 = LRUCache(3)
    cache2.put(1, "a")
    cache2.put(2, "b")
    cache2.put(3, "c")
    
    # Access key 1, making it most recent
    cache2.get(1)
    
    # Add new key - should evict key 2 (now least recent)
    cache2.put(4, "d")
    
    assert cache2.get(1) == "a", "Failed: key 1 should exist"
    assert cache2.get(2) is None, "Failed: key 2 should be evicted"
    assert cache2.get(3) == "c", "Failed: key 3 should exist"
    assert cache2.get(4) == "d", "Failed: key 4 should exist"
    print("✓ Access changes LRU order correctly")
    
    # Test 5: Capacity 1
    print("\nTest 5: Capacity 1")
    cache3 = LRUCache(1)
    cache3.put(1, "a")
    cache3.put(2, "b")  # Should evict key 1
    
    assert cache3.get(1) is None, "Failed: key 1 should be evicted"
    assert cache3.get(2) == "b", "Failed: key 2 should exist"
    print("✓ Capacity 1 works")
    
    # Test 6: Get non-existent key
    print("\nTest 6: Get non-existent key")
    cache4 = LRUCache(2)
    assert cache4.get(999) is None, "Failed: non-existent key should return None"
    print("✓ Non-existent key returns None")
    
    # Test 7: Invalid capacity
    print("\nTest 7: Invalid capacity")
    try:
        LRUCache(0)
        print("✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Invalid capacity raises ValueError: {e}")
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    test_lru_cache()