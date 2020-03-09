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
        self.auth_url = None
        self.file_handler = file_handler
        if self.token is None:
            raise ValueError("token parameter must be supplied.")

    def __str__(self):
        return u'\n\t'.format(self.links) + '\n\t'.join([u'{}:{}'.format(k, v)
                                                         for k, v in self.__dict__.items() if v])

    def _get_links(self):
        '''Returns a list of links'''
        return self.links

    def _check_download_status(self):
        pass

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
        self.token = token
        self.threads = []
        self.file_handler = file_handler
        self.file_handler.make_staging()
        super().__init__(self.file_handler, self.token)

    def _get(self, link, session):
        """Called inside each thread.
    
        Args:
            link (str): the link to download.
            session (requests.Session): a session object.
        """
        file_name = link.split('/')[-1]
        with session.get(link, allow_redirects=True, stream=True) as response:
            with open(os.path.join(
                self.file_handler.staging_path), file_name) as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

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
            response = session.post(self.url, token)
            for link in links:
                thread = threading.Thread(
                    target=_get, args=(link, ))
                self.threads.append(thread)
                thread.start()        

    def wait(self):
        """Wait for all threads to finish processesing"""
        for thead in self.threads:
            thread.wait()


class FileHandler():
    """A file handler object, capable to saving files to disk.
    
    Args:
        path (str): The destination path to save the file.
        file_extractor (obj): Object capable of extracting files.
    """
    def __init__(self, path, file_extracter):
        self.file_extracter  = file_extracter
        self.path = path
        self.staging_path = self.make_staging()

    def make_staging(self):
        """Creates the staging path.
        Uses uuid4 to create a unique path in the destination directory
        which is used as a staging area for file download/extraction.
        
        Return:
            str: Staging directory path.
        """
        if os.path.exists(self.path):
            staging_path = os.path.join(self.path, str(uuid.uuid4()))
            os.mkdir(staging_path)
            return staging_path

    def remove_staging(self):
        """Removes the staging path"""
        os.rmdir(self.staging_path)


class FileExtracter():
    pass


def main():
    pass

if __name__ == '__main__':
    main()
