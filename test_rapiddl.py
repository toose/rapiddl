import unittest
from unittest import mock
from rapiddl import Rapidgator, FileHandler
from tempfile import TemporaryDirectory, TemporaryFile


class TestRapidgator(unittest.TestCase):
    def setUp(self):
        self.token = 'mocktoken'
        self.links = ['https://example.com/some-file.part1.rar', 'https://example.com/some-file.part1.rar']
        rg = Rapidgator(self.links, 'hi')

    def test_no_token_raises_exception(self):
        '''Raises an exception when no token is provided'''
        self.assertRaises(ValueError, Rapidgator, links=self.links)


if __name__ == '__main__':
    unittest.main()
