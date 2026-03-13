"""
A pure Python LRU Cache implementation without any external dependencies.
Supports get(key) and put(key, value) with O(1) time complexity.
"""

class LRUCache:
    def __init__(self, capacity):
        """
        Initialize the LRU cache with positive capacity.
        """
        self.capacity = capacity
        self.cache = {}  # key -> node
        
        # Doubly linked list dummy nodes
        self.head = Node()  # most recently used
        self.tail = Node()  # least recently used
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get(self, key):
        """
        Get the value of the key if it exists in the cache, otherwise return -1.
        Move the accessed key to the front (most recently used).
        """
        if key in self.cache:
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return -1
    
    def put(self, key, value):
        """
        Set or insert the value if the key is not already present.
        When the cache reaches its capacity, it should invalidate the least recently used item.
        """
        if key in self.cache:
            # Update existing node
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_node(new_node)
            
            # If over capacity, remove tail (least recently used)
            if len(self.cache) > self.capacity:
                removed_node = self._pop_tail()
                del self.cache[removed_node.key]
    
    def _add_node(self, node):
        """Add a new node right after head."""
        node.prev = self.head
        node.next = self.head.next
        
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove an existing node."""
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move a node to the head (most recently used)."""
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self):
        """Remove and return the tail node (least recently used)."""
        node = self.tail.prev
        self._remove_node(node)
        return node

class Node:
    """Doubly linked list node."""
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None