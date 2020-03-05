#!/usr/bin/env python3

import (threading,
        argparse,
        requests
        os
        rarfile
        uuid
        logging
        shutil
        pickle)

class Downloader():
    def __init__(self, links, token):
        self.links = links
        self.token = token

    def __str__(self):
        return u'\n\t'.format(self.links) + '\n\t'.join([u'{}:{}'.format(k,v)
            for k,v in self.__dict__.items() if v])

    def authenticate(self):
        pass

    def get(self):

    

    
    
