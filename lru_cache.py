class _Node:
    """Doubly linked list node."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache:
    """Least Recently Used (LRU) cache with O(1) get and put.

    Data structure
    --------------
    A hash map (dict) maps keys to doubly-linked-list nodes, giving O(1)
    lookup.  The doubly linked list maintains access order: the head's
    next neighbor is the *most* recently used item and the tail's prev
    neighbor is the *least* recently used item.  Moving a node to the
    front or removing the last node are both O(1) pointer operations,
    so every get and put runs in constant time.
    """

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: dict[int, _Node] = {}
        # Sentinel head/tail simplify edge-case handling.
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    # -- internal helpers --------------------------------------------------

    def _remove(self, node: _Node) -> None:
        """Unlink a node from the list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node: _Node) -> None:
        """Insert a node right after head (most-recently-used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    # -- public API --------------------------------------------------------

    def get(self, key: int) -> int:
        """Return the value for *key*, or -1 if absent.

        Accessing a key marks it as most recently used.
        """
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        """Insert or update *key* with *value*.

        If the cache exceeds capacity, the least recently used item is
        evicted.
        """
        if key in self.cache:
            self._remove(self.cache[key])
            del self.cache[key]
        node = _Node(key, value)
        self._add_front(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
