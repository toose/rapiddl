from unittest import TestCase, mock
from tempfile import TemporaryDirectory, gettempdir
import os
import logging
import requests
import uuid

from rapiddl import main, clean_name, build_payload, make_staging, get, _get, unzip


class TestRapiddl(TestCase):
    @mock.patch('rapiddl.os.mkdir')
    def setUp(self, mock_mkdir):
        self.tempdir = '/tmp/'
        self.threads = []
        self.staging_path = make_staging(gettempdir())
        self.link = 'https://rapidgator.net/file/fc99592c0f8b17f32cf2b8258b1eb5e0/Up.in.Smoke.1978.720p.BRRip.H264.AAC-RARBG.rar.html'
        self.session = mock_session = mock.create_autospec(requests.Session)

    @mock.patch('rapiddl.os.path.exists', return_value=False)
    def test_destination_exists(self, mock_exists):
        '''Raises an exception when the destination does not exist'''
        with self.assertRaises(FileNotFoundError) as err:
            main(['-l','https//home.net', '-d', '/DoesNotExist', '-v'])
        mock_exists.assert_called_with('/DoesNotExist')

    def test_clean_name(self):
        name = clean_name(self.link)
        self.assertEqual(name, 'Up.in.Smoke.1978.720p.BRRip.H264.AAC-RARBG.rar')

    def test_build_payload(self):
        '''Checks username/password format'''
        payload = build_payload('user@email.com', 'testpass123')
        self.assertEqual(payload['LoginForm[email]'], 'user@email.com')
        self.assertEqual(payload['LoginForm[password]'], 'testpass123')

    def test_invalid_username(self):
        '''Checks that the username is an email address'''
        with self.assertRaises(ValueError) as err:
            build_payload('invalid_user', 'testpass123')

    @mock.patch('rapiddl.os.mkdir')
    def test_make_staging(self, mock_mkdir):
        '''Tests staging folder creation'''
        staging_path = make_staging(gettempdir())
        mock_mkdir.assert_called_with(staging_path)

    @mock.patch('rapiddl.os.mkdir')
    @mock.patch('rapiddl.threading.Thread')
    def test_get_method(self, mock_thread, mock_mkdir):
        '''Get method calls new Thread'''
        path = os.path.join(gettempdir(), str(uuid.uuid4())[:8])
        get(self.session, self.link, path, self.threads)
        mock_thread.assert_called_once()

    @mock.patch('rapiddl.open')
    def test__get_method(self, mock_open):
        '''Tests writing remote file to disk'''
        _get(self.session, self.link, self.staging_path)
        mock_open.assert_called()

    @mock.patch('rapiddl.rarfile.RarFile', auto_spec=True)
    def test_unzip_method(self, mock_rarfile):
        '''Unzips the contents of a .rar file'''
        mock_rarfile.return_value.__enter__.return_value.infolist.return_value = ['file1.mp4']
        file = '/path/to/archive.rar'
        destination = '/tmp/'
        unzip(file=file, path=destination)

        mock_rarfile.assert_called()
        mock_rarfile.return_value.__enter__.return_value.extract.assert_called_with('file1.mp4', path='/tmp/')

    @mock.patch('rapiddl.shutil.rmtree')
    @mock.patch('rapiddl.os.listdir', return_value=['archive.rar'])
    @mock.patch('rapiddl.os.path.exists', return_value=True)
    @mock.patch('rapiddl.make_staging', return_value='/tmp/438cab0f')
    @mock.patch('rapiddl.unzip')
    @mock.patch('rapiddl.get')
    @mock.patch('rapiddl.shutil.move')
    def test_main_method_rar_without_extraction(self, mock_move, mock_get, mock_unzip, mock_staging, mock_exists, mock_listdir, mock_rmtree):
        # rar file without extraction
        main(['-l', 'https://website/archive.rar', '-d', self.tempdir, '-u', 'user@email.com', '-p', 'testpass123'])
        mock_move.assert_called_with('/tmp/438cab0f/archive.rar', self.tempdir)

    @mock.patch('rapiddl.shutil.rmtree')
    @mock.patch('rapiddl.os.listdir', return_value=['archive.rar'])
    @mock.patch('rapiddl.os.path.exists', return_value=True)
    @mock.patch('rapiddl.make_staging', return_value='/tmp/438cab0f')
    @mock.patch('rapiddl.unzip')
    @mock.patch('rapiddl.get')
    @mock.patch('rapiddl.shutil.move')
    def test_main_method_rar_with_extraction(self, mock_move, mock_get, mock_unzip, mock_staging, mock_exists, mock_listdir, mock_rmtree):
        # rar file without extraction
        main(['-l', 'https://website/archive.rar', '-d', self.tempdir, '-u', 'user@email.com', '-p', 'testpass123', '-e'])
        mock_unzip.assert_called_with(file='/tmp/438cab0f/archive.rar', path=self.tempdir)

    @mock.patch('rapiddl.shutil.rmtree')
    @mock.patch('rapiddl.os.listdir', return_value=['video.mp4'])
    @mock.patch('rapiddl.os.path.exists', return_value=True)
    @mock.patch('rapiddl.make_staging', return_value='/tmp/438cab0f')
    @mock.patch('rapiddl.unzip')
    @mock.patch('rapiddl.get')
    @mock.patch('rapiddl.shutil.move')
    def test_main_method_mp4_without_extraction(self, mock_move, mock_get, mock_unzip, mock_staging, mock_exists, mock_listdir, mock_rmtree):
        # mp4 file without extraction
        main(['-l', 'https://website/video.mp4', '-d', self.tempdir, '-u', 'user@email.com', '-p', 'testpass123'])
        mock_move.assert_called_with('/tmp/438cab0f/video.mp4', self.tempdir)


