"""LRU Cache implementation from scratch without functools or external libs.

Uses a hash map + doubly linked list for O(1) get and put operations.
When capacity is exceeded, the least recently used item is evicted.
"""


class Node:
    """Doubly linked list node for tracking access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """LRU Cache with O(1) get and put operations.
    
    Attributes:
        capacity: Maximum number of items before eviction occurs.
    """
    
    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        # Sentinel nodes for doubly linked list
        self.head = Node(None, None)  # MRU side (most recently used)
        self.tail = Node(None, None)  # LRU side (least recently used)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """Remove a node from the linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node):
        """Add a node right after head (mark as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """Get value by key. Returns -1 if key doesn't exist.
        
        Time complexity: O(1)
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to head (mark as recently used)
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """Insert or update a key-value pair.
        
        If key exists, update value and mark as recently used.
        If key doesn't exist and cache is full, evict LRU item first.
        
        Time complexity: O(1)
        """
        if self.capacity == 0:
            return
        
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            # Add new key
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            
            # Evict if over capacity
            if len(self.cache) > self.capacity:
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
    
    def __len__(self):
        """Return current number of items in cache."""
        return len(self.cache)
    
    def __repr__(self):
        """Debug representation showing cache contents."""
        items = []
        curr = self.head.next
        while curr != self.tail:
            items.append(f"{curr.key}: {curr.value}")
            curr = curr.next
        return f"LRUCache({self.capacity}): [{', '.join(items)}]"


def test_lru_cache():
    """Test suite for LRU Cache."""
    print("=== LRU Cache Tests ===\n")
    
    # Test 1: Basic put and get
    print("Test 1: Basic put and get")
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    assert cache.get(1) == 100, "Should return 100"
    assert cache.get(2) == 200, "Should return 200"
    print("✓ Basic put/get works\n")
    
    # Test 2: Capacity eviction
    print("Test 2: Capacity eviction")
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.put(3, 300)  # Should evict key 1 (LRU)
    assert cache.get(1) == -1, "Key 1 should be evicted"
    assert cache.get(2) == 200, "Key 2 should exist"
    assert cache.get(3) == 300, "Key 3 should exist"
    print("✓ Eviction works correctly\n")
    
    # Test 3: Update existing key
    print("Test 3: Update existing key")
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.put(1, 150)  # Update key 1
    assert cache.get(1) == 150, "Key 1 should have updated value"
    assert len(cache) == 2, "Size should remain 2"
    print("✓ Update existing key works\n")
    
    # Test 4: LRU tracking with get
    print("Test 4: LRU tracking with get")
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.get(1)  # Access key 1, making it MRU
    cache.put(3, 300)  # Should evict key 2 (now LRU)
    assert cache.get(2) == -1, "Key 2 should be evicted (was LRU)"
    assert cache.get(1) == 100, "Key 1 should exist (was accessed)"
    assert cache.get(3) == 300, "Key 3 should exist"
    print("✓ LRU tracking with get works\n")
    
    # Test 5: Capacity 0
    print("Test 5: Capacity 0")
    cache = LRUCache(0)
    cache.put(1, 100)
    assert cache.get(1) == -1, "Cache with capacity 0 should not store anything"
    print("✓ Capacity 0 handled correctly\n")
    
    # Test 6: Single capacity
    print("Test 6: Single capacity")
    cache = LRUCache(1)
    cache.put(1, 100)
    assert cache.get(1) == 100
    cache.put(2, 200)  # Evicts key 1
    assert cache.get(1) == -1
    assert cache.get(2) == 200
    print("✓ Single capacity works\n")
    
    # Test 7: String keys
    print("Test 7: String keys")
    cache = LRUCache(3)
    cache.put("a", "apple")
    cache.put("b", "banana")
    cache.put("c", "cherry")
    assert cache.get("a") == "apple"
    assert cache.get("b") == "banana"
    assert cache.get("c") == "cherry"
    print("✓ String keys work\n")
    
    # Test 8: Complex scenario
    print("Test 8: Complex scenario")
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    cache.get(1)      # Order: 1 (MRU), 3, 2 (LRU) - accessing 1 makes it MRU
    cache.put(4, 4)   # Evicts 2 (LRU), Order: 4, 1, 3
    assert cache.get(2) == -1, "Key 2 should be evicted (was LRU)"
    assert cache.get(1) == 1
    assert cache.get(3) == 3
    assert cache.get(4) == 4
    print("✓ Complex scenario works\n")
    
    print("=== All tests passed! ===")


if __name__ == "__main__":
    test_lru_cache()
