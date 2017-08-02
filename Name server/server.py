import sqlite3
from socket import *
import sys
import ssl
import pickle


class ChatServer(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024):

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        self.sock.listen(10)
        self.sock.setblocking(False)
        print('Chat server started on addr {0}'.format(self.addr))
        self.sockets = [self.sock]
        self.database_adapter = ()
