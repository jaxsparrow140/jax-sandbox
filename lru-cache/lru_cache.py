"""
A Python LRU (Least Recently Used) cache implementation from scratch.
Supports get(key) and put(key, value) with O(1) time complexity.
Uses a doubly linked list and hash map for efficient operations.
"""

class Node:
    """Doubly linked list node to store key-value pairs"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """LRU Cache implementation with O(1) get and put operations"""
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with positive capacity.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Hash map: key -> Node
        
        # Doubly linked list dummy nodes
        self.head = Node(0, 0)  # Dummy head
        self.tail = Node(0, 0)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
        
    def _add_node(self, node):
        """Add a new node right after head"""
        # Insert between head and head.next
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        
    def _remove_node(self, node):
        """Remove an existing node from the linked list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
        
    def _move_to_head(self, node):
        """Move a node to the head (most recently used)"""
        self._remove_node(node)
        self._add_node(node)
        
    def _pop_tail(self):
        """Remove and return the tail node (least recently used)"""
        node = self.tail.prev
        self._remove_node(node)
        return node
        
    def get(self, key):
        """
        Get the value of the key if it exists in the cache, otherwise return -1.
        
        Args:
            key: The key to look up
            
        Returns:
            int: The value associated with the key, or -1 if not found
        """
        if key in self.cache:
            # Move the accessed node to the head (most recently used)
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return -1
        
    def put(self, key, value):
        """
        Set or insert the value for the given key.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new key-value pair
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            # If cache exceeds capacity, remove least recently used item
            if len(self.cache) > self.capacity:
                # Remove tail node (LRU)
                lru_node = self._pop_tail()
                del self.cache[lru_node.key]

# Test the implementation
if __name__ == "__main__":
    # Test case 1: Basic functionality
    print("Test 1: Basic functionality")
    lru = LRUCache(2)
    lru.put(1, 1)
    lru.put(2, 2)
    print(f"get(1): {lru.get(1)}")  # returns 1
    lru.put(3, 3)  # evicts key 2
    print(f"get(2): {lru.get(2)}")  # returns -1 (not found)
    lru.put(4, 4)  # evicts key 1
    print(f"get(1): {lru.get(1)}")  # returns -1 (not found)
    print(f"get(3): {lru.get(3)}")  # returns 3
    print(f"get(4): {lru.get(4)}")  # returns 4
    
    # Test case 2: Capacity of 1
    print("\nTest 2: Capacity of 1")
    lru = LRUCache(1)
    lru.put(1, 1)
    print(f"get(1): {lru.get(1)}")  # returns 1
    lru.put(2, 2)  # evicts key 1
    print(f"get(1): {lru.get(1)}")  # returns -1
    print(f"get(2): {lru.get(2)}")  # returns 2
    
    # Test case 3: Update existing key
    print("\nTest 3: Update existing key")
    lru = LRUCache(3)
    lru.put(1, 1)
    lru.put(2, 2)
    lru.put(3, 3)
    print(f"get(1): {lru.get(1)}")  # returns 1
    lru.put(2, 20)  # update value of key 2
    print(f"get(2): {lru.get(2)}")  # returns 20
    lru.put(4, 4)  # evicts key 3 (least recently used)
    print(f"get(3): {lru.get(3)}")  # returns -1
    print(f"get(4): {lru.get(4)}")  # returns 4
    
    # Test case 4: Edge case - capacity 0 (should raise error)
    print("\nTest 4: Edge case - capacity 0")
    try:
        lru = LRUCache(0)
    except ValueError as e:
        print(f"Expected error: {e}")
    
    # Test case 5: Access pattern to verify LRU eviction
    print("\nTest 5: Access pattern to verify LRU eviction")
    lru = LRUCache(4)
    keys = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 6]
    for key in keys:
        if key in [1, 2, 3, 4]:
            lru.put(key, key)
        else:
            lru.put(key, key)
        
    print(f"Cache state after operations: {list(lru.cache.keys())}")
    # Should have [2, 1, 5, 6] or similar with 6 being most recent
    
    # Test case 6: Performance test with large number of operations
    print("\nTest 6: Performance test")
    lru = LRUCache(100)
    import time
    start_time = time.time()
    for i in range(1000):
        lru.put(i, i * 2)
        if i % 10 == 0:
            lru.get(i - 5)
    end_time = time.time()
    print(f"Completed 1000 operations in {end_time - start_time:.4f} seconds")
    print(f"Final cache size: {len(lru.cache)}")
    
    print("\nAll tests completed!")