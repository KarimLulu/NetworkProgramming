from socket import *
import sys
import ssl

class TCPClient(object):

    def __init__(self, HOST = 'localhost', PORT = 80, BUFSIZ = 1024):
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock= socket(AF_INET, SOCK_STREAM)

    @classmethod
    def with_ssl(cls, HOST = 'localhost', PORT = 443, BUFSIZ = 1024):
        client = cls(HOST=HOST, PORT=PORT, BUFSIZ=BUFSIZ)
        client.sock = ssl.wrap_socket(client.sock)
        return client

    def conn(self):
        self.sock.connect(self.addr)
        print('Connected to {0}'.format(self.addr))

    def send(self, data):
        self.sock.sendall(bytes(data, 'utf-8'))
        print('Data is sent. Waiting for the reponse...\n')

    def recv(self):
        data = []
        chunk = self.sock.recv(self.bufsize)
        while len(chunk)>0:
            data.append(chunk)
            chunk = self.sock.recv(self.bufsize)
        return b''.join(data)


if __name__ == '__main__':
    HOST = 'en.wikipedia.org'
    PORT = 443
    page = '/wiki/Battle_of_Dunkirk'
    client = TCPClient.with_ssl(HOST, PORT, 4096)
    client.conn()
    cmd = 'GET {page} HTTP/1.1\nConnection: close\nHost: {host}\n\n'.format(host=HOST, page=page) #or use HTTP/1.0
    client.send(cmd)
    response = client.recv()
    header_separator = b'\r\n\r\n'
    posh = response.find(header_separator) # The end of the header
    #print(response[:posh].decode()) # Try to determine encoding
    charset = 'utf-8'
    with open(HOST+'.html', 'w') as f:
        f.write(response[posh+len(header_separator):].decode(charset))

    print(len(response), len(response.decode(charset)))
    print(min(response), max(response))
