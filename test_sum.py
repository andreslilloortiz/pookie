import unittest
import sum  # Importamos la librería compilada en C

class TestSumModule(unittest.TestCase):
    def test_add(self):
        self.assertEqual(sum.add(2, 3), 5)
        self.assertEqual(sum.add(-1, 1), 0)
        self.assertEqual(sum.add(7, 3), 10)

if __name__ == "__main__":
    unittest.main()
