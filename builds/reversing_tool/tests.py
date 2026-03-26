import unittest
from builds.reversing_tool.implementation import reverse_string

class TestReverseString(unittest.TestCase):
    def test_reverse_hello(self):
        self.assertEqual(reverse_string('hello'), 'olleh')

    def test_reverse_world(self):
        self.assertEqual(reverse_string('world'), 'dlrow')

    def test_reverse_empty(self):
        with self.assertRaises(ValueError):
            reverse_string('')

if __name__ == '__main__':
    unittest.main()