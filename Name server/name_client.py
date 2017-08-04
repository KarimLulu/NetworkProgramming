from socket import *
import sys
import pickle
import select
import os


class NameClient(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024, nickname = 'Username'):

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock.settimeout(2)
        try:
            self.sock.connect(self.addr)
        except:
            print('Unable to connect to {0}'.format(self.addr))
            sys.exit()
        print('Connected to remote host at {0}. Start sending messages'.format(self.addr), flush=True)
        #print(self.sock.getpeername(), self.sock.getsockname())
        print('<Me> ', flush = True, end = '')
        self.sockets = [sys.stdin, self.sock]


    def communicate(self):
        try:
            while True:
                 rlist, wlist, xlist = select.select(self.sockets, [], [])
                 for sock in rlist:
                    if sock==sys.stdin:
                        # Client would like to send something
                        data = sys.stdin.readline()
                        self.sock.send(data.encode('utf-8'))
                        print('<Me> ', flush = True, end = '')
                    else:
                        # Message from server was received
                        data = sock.recv(self.bufsize)
                        if not data:
                            print('Disconnected from the server...', file = sys.stderr)
                            sys.exit()
                        else:
                            print(data.decode('utf-8'), end = '')
                            print('<Me> ', flush = True, end = '')
        except KeyboardInterrupt:
            self.sock.close()

if __name__=='__main__':
    name_client = NameClient()
    name_client.communicate()
