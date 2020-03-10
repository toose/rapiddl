import unittest, requests
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
        self.mock_file_handler.staging_path = '/tmp/staging/'
        self.rg = Rapidgator(self.mock_file_handler, token=self.token)

    def test_no_token_raises_exception(self):
        """Raises an exception when no token is provided"""
        self.assertRaises(ValueError, Rapidgator, self.mock_file_handler)

    @mock.patch('rapiddl.Rapidgator.get')
    def test_get_method_executes_twice(self, mock_get):
        """Confirm methods in get function execte X times"""
        for link in self.links:
            self.rg.get(link)
            mock_get.assert_called_with(link)

    @mock.patch('rapiddl.Rapidgator.wait')
    def test_wait_method_calls_thread_wait(self, mock_wait):
        """wait() method calls Thread.wait()"""
        self.rg.wait()
        mock_wait.assert_called_once()
    
    @mock.patch('rapiddl.open')
    def test__get_method_calls_session_get(self, mock_open):
        """_get() method should call session.get twice"""
        mock_session = mock.create_autospec(requests.Session)
        for link in self.links:
            self.rg._get(link, mock_session)
        self.assertEqual(mock_session.get.call_count, 2)
        self.assertEqual(mock_open.call_count, 2)

    def test_clean_file_name_returns_expected_result(self):
        """_clean_file_name() properly cleans the file_name"""
        file1 = 'Spaceballs.1987.1080p.BluRay.x264.YIFY.mp4.html'
        result1 = self.rg._clean_file_name(file1)
        self.assertEqual(result1, 'Spaceballs.1987.1080p.BluRay.x264.YIFY.mp4')
        
        file2 = 'Spaceballs.1987.1080p.BluRay.x264.YIFY.mp4'
        result2 = self.rg._clean_file_name(file2)
        self.assertEqual(result2, 'Spaceballs.1987.1080p.BluRay.x264.YIFY.mp4')


class TestFileHandler(unittest.TestCase):
    @mock.patch('rapiddl.os.mkdir')
    def setUp(self, mock_mkdir):
        self.file_handler = FileHandler('/tmp/staging', None)

    @mock.patch('rapiddl.os.mkdir')
    @mock.patch('rapiddl.os.path.exists', return_value=True)
    @mock.patch('rapiddl.uuid.uuid4', return_value='b75bc907-c056-4e82-b015-c9851075721e')
    def test_make_staging(self, mock_uuid4, mock_exists, mock_mkdir):
        self.file_handler.make_staging()
        mock_uuid4.assert_called_once()
        mock_mkdir.assert_called_with('/tmp/staging/b75bc907-c056-4e82-b015-c9851075721e')

    @mock.patch('rapiddl.os.rmdir')
    def test_remove_staging(self, mock_rmdir):
        self.file_handler.remove_staging()
        mock_rmdir.assert_called_once()

    @mock.patch('rapiddl.os.path.exists', return_value=True)
    def test_destination_exists(self, mock_exists):
        """Tests if the destination path exists."""
        pass
        
    @mock.patch('rapiddl.os.path.exists', return_value=False)
    def test_destination_does_not_exist(self, mock_exists):
        """Tests if the destination path does not exists."""
        path = '/does_not_exist'
        with self.assertRaises(FileNotFoundError) as exception:
            self.file_handler.make_staging(path).should_raise()


if __name__ == '__main__':
    unittest.main()
