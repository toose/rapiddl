import threading, argparse, requests
from bs4 import BeautifulSoup
from queue import Queue

'''Downloads content from RapidGator.net for use with Plex Media server'''

def get(session, link):
    filename = link.split('/')[-1]
    response = session.get(link, allow_redirects=True)
    with open(filename, 'wb') as file:
        file.write(response.content)

def main():
    parser = argparse.ArgumentParser(description='Rapidgator downloader')
    parser.add_argument('-l', '--link', required=True, nargs='+')
    parser.add_argument('-t', '--type', required=True)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    args = parser.parse_args()

    LOGIN_URL = 'https://rapidgator.net/auth/login'
    LOGIN_PAYLOAD = {
        'LoginForm[email]': args.username, 
        'LoginForm[password]': args.password
    }

    with requests.Session() as session:
        session = requests.Session()
        post = session.post(LOGIN_URL, data=LOGIN_PAYLOAD)
        for link in args.link:
            threads = threading.Thread(target=get, args=(session, link))
        threads.start()

if __name__ == '__main__':
    main()