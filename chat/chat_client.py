from socket import *
import sys
import pickle
import select


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
        print('Client connected to the chat server at {0}. Please send messages'.format(self.addr), flush=True)
        sys.stdout.write('[Me] '); sys.stdout.flush()
        self.sockets = [sys.stdin, self.sock]
        self.nickname = nickname


    def communicate(self):
        try:
            while True:
                 rlist, wlist, xlist = select.select(self.sockets, [], [])
                 for sock in rlist:
                    if sock==sys.stdin:
                        # Client would like to send something
                        data = (self.nickname, sys.stdin.read())
                        print(data)
                        msg = pickle.loads(data)
                        self.sock.send(msg)
                        sys.stdout.write('[Me] '); sys.stdout.flush()
                    else:
                        # Message from server was received
                        data = sock.recv(self.bufsize)
                        if not data:
                            print('Disconnected...')
                            sys.exit()
                        else:
                            sys.stdout.write(data.decode('utf-8'))
                            sys.stdout.write('[Me] '); sys.stdout.flush()
        except KeyboardInterrupt:
            self.sock.close()

if __name__=='__main__':
    nickname = input('Your nickname> ')
    chat_client = ChatClient(nickname = nickname)
    chat_client.communicate()
