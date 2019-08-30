#!/usr/bin/env python3

import threading, argparse, requests, os, rarfile, uuid, shutil, logging, pickle

'''Downloads content from RapidGator.net for use with Plex Media server'''

def get(session, path, link, index=None):
    '''Retrieves content from RapidGator.net
    
    Downloads a file from RapidGator. If there are multiple links
    to download content from, prepend an index number to the
    filename so we can decompress the files in the correct order
    later in the script.

    Args:
        session: A requests.Session object.
        path: The destination path to download the file.
        link: The url to download content from.
        index: If the total number of links is greater than 1, prepend
               the filename with an order number -- used later for 
               decompressing multi-part rar files.
               if the total number of links is equal to 1, omit
               prepending the filename with a number
    '''
    if link[-5:] == '.html':
        link = link[:-5]
    filename = link.split('/')[-1]
    if index is not None:
        filename = str(index) + filename
    with session.get(link, allow_redirects=True, stream=True) as response:
        with open(os.path.join(path, filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

def extract(file, path, video_formats):
    video_files = []
    if file[-4:] == '.rar':
        with rarfile.RarFile(os.path.join(path, file)) as rf:
            for rar_file in rf.infolist():
                if rar_file.filename[-4:] in video_formats:
                    rf.extract(rar_file, path=path)
                    video_files.append(os.path.join(path, rar_file.filename))
    return video_files

def make_staging(path):
    staging_dir = os.path.split(path)[0]
    if not os.path.exists(staging_dir):
        os.mkdir(staging_dir)
    if not os.path.exists(path):
        os.mkdir(path)

def verify(staging_path, files):
    '''Verifies that the downloaded files are named appropriately.

    When dealing with multi-part .rar files, the files need to have the same
    base name in order to extract. If they do not, the extraction will fail. 
    
    This checks to see if the characters 1-5 of the first 2 files are the 
    same. If they are, it returns the original list untouched. If they are 
    different, it renames each one to 'download.part<n>.rar' where n is the 
    part number.

    The reason we use 1-5 and not 0-5 is becuase the index of the file
    being downloaded is prepended to the file so that we can name them
    appropriately in order to extract multi-part rar files in the correct order.

    Args:
        files: a list of files to check.

    Returns:
        A list of files.
    '''
    if files[0][1:5] != files[1][1:5]:
        for i, file in enumerate(files):
            os.rename(os.path.join(staging_path, file), 
                        os.path.join(staging_path, 'download.part{}.rar'.format(i + 1)))
        files = os.listdir(staging_path)
    return files

def main():
    parser = argparse.ArgumentParser(description='Rapidgator downloader')
    parser.add_argument('-l', '--link', nargs='+')
    parser.add_argument('-d', '--dest', required=True)
    parser.add_argument('-f', '--file')
    parser.add_argument('-n', '--filename')
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

    # Parameter checking (fail fast)
    if not os.path.exists(args.dest):
        raise FileNotFoundError(args.dest, ' does not exist')
    if not args.username or not args.password:
        logger.info('Credentials not supplied -- searching for auth file')
        if os.path.exists('auth'):
            with open('auth', 'rb') as auth_file:
                LOGIN_PAYLOAD = pickle.load(auth_file)
                logger.info('Authentication file imported')
        else:
            raise FileNotFoundError('Authentication file not found')

    # Args.file represents a file with a list of links within
    if args.file:
        links = []
        with open(args.file, 'r') as file:
            for line in file:
                links.append(line.rstrip('\n'))
    else:
        links = args.link

    threads = []
    video_formats = ['.mkv','.mp4']
    zip_formats = ['.rar']
    staging_path = os.path.join(os.getcwd(), 'staging', str(uuid.uuid4()))
    make_staging(staging_path)
    logger.info('Staging path created')
    with requests.Session() as session:
        post = session.post(LOGIN_URL, data=LOGIN_PAYLOAD)
        logger.info('Authentication successful')
        for index, link in enumerate(links):
            if len(links) == 1:
                index = None
            thread = threading.Thread(target=get, 
                args=(session, staging_path, link, index))
            threads.append(thread)
            thread.start()
            logger.info('Downloading file from {}'.format(link))
        for thread in threads:
            thread.join()
        logger.info('Downloading complete')
    files = os.listdir(staging_path)
    files.sort()
    if len(files) > 1:
        files = verify(staging_path, os.listdir(staging_path))
    # Extract archives
    if files[0][-4:] in zip_formats:
        video_files = extract(files[0], staging_path, video_formats)
        logger.info('File extraction complete')
    # Move files that do not need to be decompressed
    elif files[0][-4:] in video_formats:
        video_files = [os.path.join(staging_path, files[0])]
    for index, file in enumerate(video_files):
        if args.filename:
            # If args.filename is provided and there are multiple videos, 
            # append an index number so as not to overwrite each new file
            # while moving them.
            if len(video_files) > 1:
                filename = "{}.{}".format(args.filename + str(index + 1), file[-3:])
            else:
                filename = "{}.{}".format(args.filename, file[-3:])
            shutil.move(file, os.path.join(args.dest, filename))
        else:
            shutil.move(file, args.dest)
    logger.info('File moved successfully')
    shutil.rmtree(staging_path)
    logger.info('Staging folder removed')

if __name__ == '__main__':
    main()