#!/usr/bin/env python3

import threading, argparse, requests, os, rarfile, uuid, shutil, logging

'''Downloads content from RapidGator.net for use with Plex Media server'''

def get(session, link, path):
    filename = link.split('/')[-1]
    response = session.get(link, allow_redirects=True)
    with open(os.path.join(path, filename), 'wb') as file:
        file.write(response.content)

def extract(file, path, video_formats):
    if file[-4:] == '.rar':
        with rarfile.RarFile(os.path.join(path, file)) as rf:
            for file in rf.infolist():
                if file.filename[-4:] in video_formats:
                    rf.extract(file, path=path)
                    video_file = os.path.join(path, file.filename)
        return video_file

def make_staging(path):
    staging_dir = os.path.split(path)[0]
    if not os.path.exists(staging_dir):
        os.mkdir(staging_dir)
    if not os.path.exists(path):
        os.mkdir(path)

def main():
    parser = argparse.ArgumentParser(description='Rapidgator downloader')
    parser.add_argument('-l', '--link', required=True, nargs='+')
    parser.add_argument('-d', '--dest', required=True)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('-v', '--verbose', action='count')
    args = parser.parse_args()

    if args.verbose == None:
        log_level = logging.ERROR
    elif args.verbose == 1:
        log_level = logging.WARN
    elif args.verbose == 2:
        log_level = logging.INFO
    elif args.verbose > 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('rapiddl.main')

    LOGIN_URL = 'https://rapidgator.net/auth/login'
    LOGIN_PAYLOAD = {
        'LoginForm[email]': args.username,
        'LoginForm[password]': args.password
    }

    if not os.path.exists(args.dest):
        raise FileNotFoundError(args.dest, ' does not exist')

    threads = []
    video_formats = ['.mkv','.mp4']
    staging_path = os.path.join(os.getcwd(), 'staging', str(uuid.uuid4()))
    make_staging(staging_path)
    logger.info('Staging path created')
    with requests.Session() as session:
        session = requests.Session()
        post = session.post(LOGIN_URL, data=LOGIN_PAYLOAD)
        logger.info('Authentication successful')
        for link in args.link:
            thread = threading.Thread(target=get, args=(session, link, staging_path))
            threads.append(thread)
            thread.start()
            logger.info('Downloading file from {}'.format(link))
        for thread in threads:
            thread.join()
        logger.info('Downloading complete')
    files = os.listdir(staging_path)
    files.sort()
    if files[0][-4:] in ['.rar']:
        file = extract(files[0], staging_path, video_formats)
        logger.info('File extraction complete')
    elif files[0][-4:] in video_formats:
        file = os.path.join(staging_path, files[0])
    elif files[0][-5:] == '.html':
        os.rename(os.path.join(staging_path, files[0]), 
                  os.path.join(staging_path, files[0][:-5]))
        file = os.path.join(staging_path, files[0][:-5])
    shutil.move(file, args.dest)
    logger.info('File moved successfully')
    shutil.rmtree(staging_path)
    logger.info('Staging folder removed')

if __name__ == '__main__':
    main()