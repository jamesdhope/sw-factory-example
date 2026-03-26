import unittest
from unittest.mock import patch
from main import parse_arguments, main
import sys


class TestMainApp(unittest.TestCase):
    @patch('sys.argv', ['main.py', '-c', 'London', '-u', 'C', '-v'])
    def test_parse_arguments(self):
        args = parse_arguments()
        self.assertEqual(args.city, 'London')
        self.assertEqual(args.units, 'C')
        self.assertTrue(args.verbose)

    @patch('sys.argv', ['main.py', '-c', 'New York', '-u', 'F'])
    @patch('builtins.print')
    def test_main(self, mock_print):
        main()
        mock_print.assert_any_call('Weather for New York: ...')


if __name__ == '__main__':
    unittest.main()
