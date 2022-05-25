import os
import unittest
import sys

path = os.path.join(os.getcwd(), "src")
sys.path.insert(0, path)
print(path)
import scraper as sc


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()

