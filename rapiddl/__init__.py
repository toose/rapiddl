#!/usr/sbin/env python3
import argparse
import os
import sys
import shutil
import logging
import uuid
import re
import threading
import requests
import rarfile


logger = logging.getLogger('rapiddl.main')

def clean_name(link):
    '''Cleans a file name, stripping it it's base url.
    
    Args:
        link (str): a link/url to clean

    Returns:
        (str): a suitable file name
    '''
    if link[-5:] == '.html':
        link = link[:-5]
    file_name = link.split('/')[-1]
    logger.info(f' file name: {file_name}')
    return file_name

def build_payload(username, password):
    '''Returns authentication information in the form of dict.

    Args:
        username (str): the username to authenticate with
        password (str): the password to authenticate with

    Returns:
        (dict): login payload
    '''

    if not re.match(r'[^@]+@[^@]+\.[^@]+', username):
        raise ValueError('Username is not a valid email address.')
    return {'LoginForm[email]': username,
            'LoginForm[password]': password}

def make_staging(destination):
    '''Creates a staging directory based off uuid.uuid4[:8] and returns
    the path as a string.
    
    Args:
        destination (str): the original destination path.
    Returns:
        (str): staging path
    '''
    guid = str(uuid.uuid4())[:8]
    staging_path = os.path.join(destination, guid)
    os.mkdir(staging_path)
    logger.info(f' staging path: {staging_path}')
    return staging_path

def parse_args(args):
    '''Parses arguemnts using the argparse package.

    Args:
        args (list): arguments passed from sys.argv

    Returns:
        argparse.NameSpace
    '''
    parser = argparse.ArgumentParser(description='Rapidgator downloader')
    parser.add_argument('-l', '--link', nargs='+')
    parser.add_argument('-d', '--destination', required=True)
    parser.add_argument('-f', '--file')
    parser.add_argument('-e', '--extract', nargs='?', default=False, const=True)
    parser.add_argument('-n', '--filename')
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('-v', '--verbose', action='count')
    return parser.parse_args(args)

def get(session, link, path, threads):
    '''Uses thread objects to concurrently download the remote file(s).
    
    Args:
        session (requests.Session): a valid session object
        link (str): a valid rapidgator link
        path (str): the destination path to download the file(s)
        threads (list): threading.Thread list
    '''
    thread = threading.Thread(target=_get, args=(session, link, path))
    threads.append(thread)
    thread.start()
    

def _get(session, link, path):
    '''Encapsulates the process of fetching and saving the file(s)
    to disk.

    Args:
        session (requests.Session): a valid session object
        link (str): a valid rapidgator link
        path (str): the destination path to download the file(s)
    '''
    file_name = clean_name(link)
    logger.info(f' downloading file from: {link}')
    with session.get(link, allow_redirects=True, stream=True) as response:
        with open(os.path.join(path, file_name), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

def unzip(file, path):
    '''Unzips files with the .rar extension

    Args:
        file: full path to the file that you want to extract
        path (str): full path to the zip file
    '''
    file = os.path.join(path, file)
    file_name = file.split(os.path.sep)[-1]
    try:
        with rarfile.RarFile(file, crc_check=False) as rf:
            for rar_file in rf.infolist():
                rf.extract(rar_file, path=path)
                logging.info(f' extracting {file_name} to {path}')
    except Exception as err:
        logger.warning(str(err))


def main(args):
    parser = parse_args(args)

    if parser.verbose == None:
        log_level = logging.ERROR
    elif parser.verbose == 1:
        log_level = logging.WARN
    elif parser.verbose == 2:
        log_level = logging.INFO
    elif parser.verbose > 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)

    if not os.path.exists(parser.destination):
        raise FileNotFoundError(f'{parser.destination} does not exist.')
    else:
        staging_path = make_staging(parser.destination)

    threads = []
    ZIP_FORMATS = ['.rar']
    VIDEO_FORMATS = ['.mkv','.mp4']
    LOGIN_URL = 'https://rapidgator.net/auth/login'
    LOGIN_PAYLOAD = build_payload(parser.username,
                                  parser.password)

    with requests.Session() as session:
        post = session.post(LOGIN_URL, data=LOGIN_PAYLOAD)
        for link in parser.link:
            get(session, link, staging_path, threads)
        for thread in threads:
            thread.join()
    for file in os.listdir(staging_path):
        full_path = os.path.join(staging_path, file)
        if file[-4:] in ZIP_FORMATS:
            if parser.extract:
                logger.info(f' extracting files to {parser.destination}')
                unzip(file=full_path, path=parser.destination)
            else:
                shutil.move(full_path, parser.destination)
        else:
            try:
                shutil.move(full_path, parser.destination)
                logger.info(f' {file} moved to {parser.destination}')
            except Exception as err:
                logger.error(str(err))
    shutil.rmtree(staging_path)
    logger.info(f' removing staging directory: {staging_path}')


if __name__ == '__main__':
    main(sys.argv[1:])
