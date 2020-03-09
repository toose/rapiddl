import unittest
from unittest import mock
from rapiddl import Rapidgator, FileHandler
from tempfile import TemporaryDirectory, TemporaryFile


class TestRapidgator(unittest.TestCase):
    def setUp(self):
        self.token = {'LoginForm[email]': 'name@email.com', 
                      'LoginForm[password]': 'TestPass123'}
        self.links = ['https://example.com/some-file.part1.rar',
                      'https://example.com/some-file.part2.rar']
        
        self.mock_file_handler = mock.create_autospec(FileHandler)
        self.rg = Rapidgator(self.mock_file_handler, token=self.token)

    def test_no_token_raises_exception(self):
        '''Raises an exception when no token is provided'''
        self.assertRaises(ValueError, Rapidgator, self.mock_file_handler)

    @mock.patch('rapiddl.Rapidgator.get')
    def test_get_method_executes_twice(self, mock_get):
        """Confirm methods in get function execte X times"""
        for link in self.links:
            self.rg.get(link)
            mock_get.assert_called_with(link)

        
    



class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.file_handler = FileHandler('/tmp', None)

    @mock.patch('rapiddl.os.path.exists', return_value=True)
    @mock.patch('rapiddl.os.mkdir')
    @mock.patch('rapiddl.uuid.uuid4', return_value='b75bc907-c056-4e82-b015-c9851075721e')
    def test_make_staging(self, mock_uuid4, mock_mkdir, mock_exists):
        self.file_handler._make_staging()
        mock_uuid4.assert_called_once()
        mock_mkdir.assert_called_once()

    @mock.patch('rapiddl.os.rmdir')
    def test_remove_staging(self, mock_rmdir):
        self.file_handler._remove_staging()
        mock_rmdir.assert_called_once()


if __name__ == '__main__':
    unittest.main()
