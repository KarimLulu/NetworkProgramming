from socket import *
import sys
import pickle
import select
import os
from threading import Thread, Lock, current_thread

class MyThread(Thread):

    def __init__(self, name, func, *args, **kwargs):
        super().__init__()
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs


    def run(self):
        self.rez = self.func(*self.args, **self.kwargs)


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
                self.clients.append(client_sock)
                print("Client {0} connected".format(addr))
                msg = 'Client {0} entered our chatting room\n'.format(addr)
                self.broadcast(client_sock, msg)
            except BlockingIOError:
                pass


    def process_message(self):
        while True:
            if self.clients:
                for client in self.clients:
                    try:
                        data = client.recv(self.bufsize)
                        if data:
                            # data is a tuple of the form: (nickname, message_from_client)
                            nickname, msg = pickle.loads(data)
                            msg_to_broadcast = "\r<{0}> {1}".format(nickname, msg)
                            self.broadcast(client, msg_to_broadcast)
                        else:
                            msg = 'Client {0} is offline\n'.format(client.getpeername())
                            self.broadcast(client, msg)
                            if client in self.clients:
                                self.clients.remove(client)
                    except BlockingIOError:
                        pass


    def broadcast(self, new_socket, msg = ''):
        for sock in self.clients:
            if sock != new_socket:
                try:
                    # '\r' is needed to owerwrite the last line (for example in progress bars)
                    sock.send(bytes(msg, 'utf-8'))
                except:
                    print('Broken socket - ' + str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
                    sock.close()
                    if sock in self.clients:
                        self.clients.remove(sock)

if __name__=='__main__':
    chat_server = ChatServer()
    chat_server.serve()
