from socket import *
import sys
import ssl
from urllib.parse import urlparse
import re
import chardet


protocol_port_mapping = {
                                'http': 80,
                                'https': 443
                            }
DEFAULT_PORT = 80
DEFAULT_SCHEME = 'http'
BUFSIZ = 4096
REQUEST_PATTERN = '{method} {page} HTTP/1.1\nConnection: close\nHost: {host}\n\n'
HEADER_SEPARATOR = b'\r\n\r\n'
REGEXP_ENCODING = r'charset=([\w.-]+)(?:;|\r\n|$)'
DEFAULT_ENCODING = 'utf-8'


class Response(object):
    def __init__(self, response_headers, raw_content, encoding):
        self.response_headers = response_headers
        self.raw = raw_content
        self.encoding = encoding


    @property
    def text(self):
        encoding = self.encoding
        if not encoding:
            encoding = self.guessed_encoding
        return self.raw.decode(encoding)


    @property
    def guessed_encoding(self):
        return chardet.detect(self.raw)['encoding']


class HTTPClient(object):

    def __init__(self, HOST = 'localhost', PORT = 80, BUFSIZ=BUFSIZ):
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock= socket(AF_INET, SOCK_STREAM)


    @classmethod
    def with_ssl(cls, HOST = 'localhost', PORT = 443, BUFSIZ=BUFSIZ):
        client = cls(HOST=HOST, PORT=PORT, BUFSIZ=BUFSIZ)
        client.sock = ssl.wrap_socket(client.sock)
        return client


    def conn(self):
        self.sock.connect(self.addr)
        print('Connected to {0}'.format(self.addr))


    def send(self, data):
        self.sock.sendall(bytes(data, 'utf-8'))
        print('Data is sent. Waiting for the reponse...\n')


    @classmethod
    def get(cls, url):
        if '//' not in url:
            url = '{scheme}://{url}'.format(scheme=DEFAULT_SCHEME, url=url)
        url_parts = urlparse(url)
        PORT = protocol_port_mapping.get(url_parts.scheme, DEFAULT_PORT)
        HOST = url_parts.hostname
        if PORT == 443:
            client = cls.with_ssl(HOST=HOST, PORT=PORT)
        else:
            client = cls(HOST=HOST, PORT=PORT)
        client.conn()
        path = url_parts.path
        if not path:
            path = '/'
        GET_REQUEST = REQUEST_PATTERN.format(method='GET', page=path, host=HOST)
        client.send(GET_REQUEST)
        raw_response = client.recv()
        response = client._build_response(raw_response)
        return response


    def _build_response(self, raw_response):
        headers_end_idx = raw_response.find(HEADER_SEPARATOR)                # The end of the header
        content_start_idx = headers_end_idx+len(HEADER_SEPARATOR)
        content = raw_response[content_start_idx:]
        response_headers = raw_response[:headers_end_idx].decode('iso-8859-1')  #Parses only RFC2822 headers, then use email.parser
        rez = re.findall(REGEXP_ENCODING, response_headers, re.MULTILINE)
        if rez:
            encoding = rez[0].lower()
        else:
            encoding = None
        return Response(response_headers, content, encoding)


    def recv(self):
        data = []
        chunk = self.sock.recv(self.bufsize)
        while len(chunk)>0:
            data.append(chunk)
            chunk = self.sock.recv(self.bufsize)
        return b''.join(data)


if __name__ == '__main__':
    url = 'google.com.ua'
    r = HTTPClient.get(url)
    with open('Dunkirk'+'.html', 'w') as f:
        f.write(r.text)
    print(r.response_headers)
