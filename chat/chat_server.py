from socket import *
import sys
import pickle
import select


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


    def serve(self):
        try:
            while True:
                rlist, wlist, xlist = select.select(self.sockets, [], [], 0)
                for sock in rlist:
                    if sock == self.sock:
                        # New connection arrived
                        client_sock, addr = self.sock.accept()
                        #client_sock.setblocking(False)
                        self.sockets.append(client_sock)
                        print("Client {0} connected".format(addr))
                        msg = 'Client {0} entered our chatting room\n'.format(addr)
                        self.broadcast(client_sock, msg)
                    else:
                        # Client sent something
                        try:
                            data = sock.recv(self.bufsize)
                            if data:
                                # data is a tuple of the form: (nickname, message_from_client)
                                nickname, msg = pickle.loads(data)
                                msg_to_broadcast = "\r<{0}> {1}".format(nickname, msg)
                                self.broadcast(sock, msg_to_broadcast)
                            else:
                                self.sockets.remove(sock)
                                msg = 'Client {0} is offline\n'.format(sock.getpeername())
                                self.broadcast(sock, msg)
                        except Exception as error:
                            self.sockets.remove(sock)
                            print(str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
                            msg = 'Smth terrible happened. Client {0} is offline'.format(sock.getpeername())
                            self.broadcast(sock, msg)
                            continue
        except KeyboardInterrupt:
            self.sock.close()


    def broadcast(self, new_socket, msg = ''):
        for sock in self.sockets:
            if sock != self.sock and sock!=new_socket:
                try:
                    # '\r' is needed to owerwrite the last line (for example in progress bars)
                    sock.send(bytes(msg, 'utf-8'))
                except:
                    print('Broken socket - ' + str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
                    sock.close()
                    if sock in self.sockets:
                        self.sockets.remove(new_socket)

if __name__=='__main__':
    chat_server = ChatServer()
    chat_server.serve()
