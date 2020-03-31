#!/usr/bin/env python3

import threading
import argparse
import os
import rarfile
import uuid
import logging
import shutil
import pickle
import requests


class Downloader():
    """Base object. Inherit to make subclasses for other file hosting 
    websites
    """
    def __init__(self, file_handler, token=None):
        self.token = token
        self.file_handler = file_handler
        self.threads = []
        if self.token is None:
            raise ValueError("token parameter must be supplied.")

    def __str__(self):
        return u'\n\t'.format(self.links) + '\n\t'.join([u'{}:{}'.format(k, v)
                                                         for k, v in self.__dict__.items() if v])

    def get(self, uri, token):
        """Authenticate and download files"""
        pass


class Rapidgator(Downloader):
    """An object which encapculates the process of authenticating against
    rapidgator.net as well as downloading one or more files.
    
    Args:
        links (list): a list of links.
        token (str): token information needed to authenticate to the
                     remote server
    """
    def __init__(self, file_handler, token=None):
        self.auth_url = 'https://rapidgator.net/auth/login'
        super().__init__(self.file_handler, self.token)
        
    def _get(self, link, session):
        """Worker function called inside each thread.
    
        Args:
            link (str): the link to download.
            session (requests.Session): a session object.
        """
        file_name = self._clean_file_name(link.split('/')[-1])
        with session.get(link, allow_redirects=True, stream=True) as response:
            with open(os.path.join(
                self.file_handler.staging_path, file_name), 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

    def _clean_file_name(self, file_name):
        """Removes .html from the end of the file name, if necessary.
        
        Args:
            file_name (str): the filename to clean.

        Return:
            str: a cleaned filename.
        """
        if '.html' in file_name:
           return file_name[:-5]
        return file_name

    def get(self, link, token=None):
        """Downloads a file from RapidGator.

        Args:
            link (str): a rapidgator url.
            token (str): used to authenticate the get method with
                rapidgator.

        Returns:
            session: requests.Session object.
        """
        if token is None:
            token = self.token
        with requests.Session() as session:
            response = session.post(self.auth_url, token)
            thread = threading.Thread(
                target=self._get, args=(link, session))
            self.threads.append(thread)
            thread.start()

    def wait(self):
        """Wait for all threads to finish processesing"""
        for thread in self.threads:
            thread.join()


class FileHandler():
    """A file handler object to saving files to disk.
    
    Args:
        path (str): the destination path to save the file.
        file_extractor (obj): object capable of extracting files.
    """
    def __init__(self, path, file_extractor):
        self.path = path
        self.file_extractor = file_extractor
        self.staging_path = self.make_staging()

    def is_compressed(self, file):
        compression_formats = ['.rar.', '.zip', '.7z']
        if file[-4:] in compression_formats:
            return True
        return False


    def make_staging(self, path=None):
        """Creates the staging path.
        Uses uuid4 to create a unique path in the destination directory
        which is used as a staging area for file download/extraction.
        
        Return:
            str: staging directory path.
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError("Destination path does not exist.")
        if path is None:
            path = self.path
        staging_path = os.path.join(self.path, str(uuid.uuid4()))
        os.mkdir(staging_path)
        return staging_path
        

    def remove_staging(self):
        """Removes the staging path"""
        os.rmdir(self.staging_path)


class FileExtracter():
    def __init__():
        pass

    def extract():
        pass


def main():
    token = {'LoginForm[email]': 'metsfan2152@gmail.com',
             'LoginForm[password]': 'Wogman2152'}
    destination_path = '/tmp/staging'
    link = 'https://rapidgator.net/file/21f84529c90684a59903b7cd9d8a72b1/Spaceballs.1987.1080p.BluRay.x264.YIFY.mp4.html'

    fh = FileHandler(destination_path, None)
    rg = Rapidgator(fh, token)
    rg.get(link)
    rg.wait()
    
    for file in os.listdir(rg.file_handler.staging_path):
        if rg.file_handler.is_compressed(file):
            rg.file_handler

    # clean up
    rg.file_handler.remove_staging()

if __name__ == '__main__':
    main()
