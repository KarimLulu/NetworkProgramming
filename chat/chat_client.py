from socket import *
import sys
import pickle
import select
import os


class ChatClient(object):

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
        print('<Me> ', flush = True, end = '')
        self.sockets = [sys.stdin, self.sock]
        self.nickname = nickname


    def communicate(self):
        try:
            while True:
                 rlist, wlist, xlist = select.select(self.sockets, [], [])
                 for sock in rlist:
                    if sock==sys.stdin:
                        # Client would like to send something
                        data = (self.nickname, sys.stdin.readline())
                        msg = pickle.dumps(data)
                        self.sock.send(msg)
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
    nickname = input('Your nickname> ')
    chat_client = ChatClient(nickname = nickname)
    chat_client.communicate()
