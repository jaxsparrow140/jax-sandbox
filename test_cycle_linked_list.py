import unittest

from cycle_linked_list import LinkedList, Node, detect_cycle_start


class TestCycleLinkedList(unittest.TestCase):
    def test_cycle_starts_at_third_node(self):
        ll = LinkedList([1, 2, 3, 4, 5])
        entry = ll.node_at(2)  # 3rd node
        ll.create_cycle(2)

        detected = detect_cycle_start(ll.head)
        self.assertIs(detected, entry)
        self.assertEqual(detected.value, 3)

    def test_no_cycle_returns_none(self):
        ll = LinkedList([1, 2, 3])
        self.assertIsNone(detect_cycle_start(ll.head))

    def test_cycle_at_head(self):
        ll = LinkedList([1, 2, 3])
        head = ll.node_at(0)
        ll.create_cycle(0)
        self.assertIs(detect_cycle_start(ll.head), head)

    def test_single_node_no_cycle(self):
        ll = LinkedList([1])
        self.assertIsNone(detect_cycle_start(ll.head))

    def test_single_node_self_cycle(self):
        n = Node(1)
        n.next = n
        self.assertIs(detect_cycle_start(n), n)

    def test_empty_list(self):
        self.assertIsNone(detect_cycle_start(None))

    def test_node_at_out_of_range(self):
        ll = LinkedList([1])
        with self.assertRaises(IndexError):
            ll.node_at(1)


if __name__ == "__main__":
    unittest.main()
