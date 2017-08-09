from socket import *
import sys
import pickle
import select
import os
from threading import Thread, Lock, current_thread

#from config import DB_PATH


class MyThread(Thread):

    def __init__(self, name, func, *args, **kwargs):
        super().__init__()
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs


    def run(self):
        self.rez = self.func(*self.args, **self.kwargs)


class Connection(object):

    def __init__(self, sock):
        self.sock = sock
        self.nickname = None


    def __getattr__(self, attr):
        return getattr(self.sock, attr)


class ChatServer(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024):

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        self.sock.listen(10)
        print('Chat server started on addr {0}'.format(self.addr))
        self.clients = []


    def serve(self):
        new_conn = MyThread(name = 'Process new connections', func = self.proccess_connection)
        handle_msg = MyThread(name = 'Process data from the client', func = self.process_message)
        new_conn.daemon = True
        handle_msg.daemon = True
        new_conn.start()
        handle_msg.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.sock.close()
            sys.exit()


    def proccess_connection(self):
        while True:
            try:
                client_sock, addr = self.sock.accept()
                client_sock.setblocking(False)
                conn = Connection(client_sock)
                print("Client {0} connected".format(addr))
                conn.nickname = addr
                self.clients.append(conn)
            except BlockingIOError:
                pass


    def process_message(self):
        while True:
            if self.clients:
                for client in self.clients:
                    try:
                        data = client.recv(self.bufsize)
                        if data:
                            msg = pickle.loads(data)
                            if r'\username' in msg:
                                username = msg.split(r'\username', 1)[-1].strip()
                                client.nickname = username
                                msg_to_broadcast = 'Client `{0}` entered our chatting room\n'.format(client.nickname)
                            else:
                                msg_to_broadcast = "\r<{0}> {1}".format(client.nickname, msg)
                            self.broadcast(client, msg_to_broadcast)
                        else:
                            msg = 'Client {0} is offline\n'.format(client.nickname)
                            self.broadcast(client, msg)
                            if client in self.clients:
                                self.clients.remove(client)
                    except BlockingIOError:
                        pass


    def broadcast(self, new_client, msg = ''):
        for client in self.clients:
            if client != new_client:
                try:
                    # '\r' is needed to owerwrite the last line (for example in progress bars)
                    client.send(bytes(msg, 'utf-8'))
                except:
                    #print('Broken socket - ' + str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
                    client.close()
                    if client in self.clients:
                        self.clients.remove(client)


    def get_username(self, addr):
        with open(DB_PATH, 'rb+') as f:
            db = pickle.load(f)
        return db.get(addr)


if __name__=='__main__':
    HOST = 'localhost'#'0.0.0.0'
    chat_server = ChatServer(HOST=HOST)
    chat_server.serve()
