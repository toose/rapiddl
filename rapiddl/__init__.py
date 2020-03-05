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
    def __init__(self, links, file_handler, token=None):
        self.links = links
        self.token = token
        self.file_handler = file_handler

    def __str__(self):
        return u'\n\t'.format(self.links) + '\n\t'.join([u'{}:{}'.format(k, v)
                                                         for k, v in self.__dict__.items() if v])

    def _get_links(self):
        '''Returns a list of links'''
        return self.links

    def _check_download_status(self):
        pass

    def authenticate(self, uri, token):
        pass

    def download(self, link, destination):
        pass


class Rapidgator(Downloader):
    ''''''
    def __init__(self, links, token=None):
        self.links = links
        self.token = token
        if self.token is None:
            raise ValueError("token parameter not supplied.")
        super(Rapidgator, self).__init__(self.links, self.token)
    

class FileHandler():
    def __init__(self, file_extracter):
        file_extracter  = file_extracter


class FileExtracter():
    pass


def main():
    pass

if __name__ == '__main__':
    main()