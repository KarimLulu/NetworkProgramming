from socket import *
import sys
import pickle
import select
import os
from threading import Thread, Lock, current_thread

from mthr_server import MyThread
from config import DB_PATH


class ChatClient(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024, nickname = 'Username'):

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        try:
            self.sock.connect(self.addr)
        except:
            print('Unable to connect to {0}'.format(self.addr))
            sys.exit()
        print('Connected to remote host at {0}. Start sending messages'.format(self.addr), flush=True)
        #print(self.sock.getpeername(), self.sock.getsockname())
        print('<Me> ', flush = True, end = '')
        self.nickname = nickname
        self.update_contacts()
        self.e = None


    def communicate(self):
        incoming = MyThread(name = 'Process incoming messages', func = self.process_input)
        outcoming = MyThread(name = 'Process outcoming messages', func = self.send_message)
        incoming .daemon = True
        outcoming.daemon = True
        incoming .start()
        outcoming.start()
        try:
            while True:
                if self.e:
                    raise self.e
                pass
        except KeyboardInterrupt:
            self.sock.close()


    def process_input(self):
        while True:
            try:
                data = self.sock.recv(self.bufsize)
                if not data:
                    print('Disconnected from the server...', file = sys.stderr, flush = True)
                    self.e = SystemExit
                else:
                    print(data.decode('utf-8'), end = '')
                    print('<Me> ', flush = True, end = '')
            except BlockingIOError:
                pass


    def send_message(self):
        while True:
            try:
                user_input = sys.stdin.readline()
                data = (self.nickname, user_input)
                msg = pickle.dumps(data)
                self.sock.send(msg)
                print('<Me> ', flush = True, end = '')
            except Exception as error:
                print(error)
                pass


    def update_contacts(self):
        with open(DB_PATH, 'rb+') as f:
            db = pickle.load(f)
            db[self.sock.getsockname()] = self.nickname
            f.seek(0)
            pickle.dump(db, f)
            f.truncate()


if __name__=='__main__':
    nickname = input('Your nickname> ')
    chat_client = ChatClient(nickname = nickname)
    chat_client.communicate()
