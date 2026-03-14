import unittest

from r2_score import r2_score


class TestR2Score(unittest.TestCase):
    def test_example(self):
        y_true = [3, -0.5, 2, 7]
        y_pred = [2.5, 0.0, 2, 8]
        self.assertAlmostEqual(r2_score(y_true, y_pred), 0.9486081370, places=9)

    def test_perfect(self):
        y_true = [1, 2, 3]
        y_pred = [1, 2, 3]
        self.assertEqual(r2_score(y_true, y_pred), 1.0)

    def test_constant_y_true_perfect(self):
        y_true = [5, 5, 5]
        y_pred = [5, 5, 5]
        self.assertEqual(r2_score(y_true, y_pred), 1.0)

    def test_constant_y_true_imperfect(self):
        y_true = [5, 5, 5]
        y_pred = [5, 4, 6]
        self.assertEqual(r2_score(y_true, y_pred), 0.0)

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            r2_score([1, 2], [1])

    def test_empty(self):
        with self.assertRaises(ValueError):
            r2_score([], [])


if __name__ == "__main__":
    unittest.main()
