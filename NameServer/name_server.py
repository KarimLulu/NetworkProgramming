import sqlite3
from socket import *
import sys
import os
import ssl
import pickle
import shlex
import select
from db_adapter import Service, DatabaseAdapter, DSN
from arg_parser import parser


class NameServer(object):

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
        self.database_adapter = DatabaseAdapter(DSN)
        self.parser = parser


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
                    else:
                        # Client sent something
                        try:
                            data = sock.recv(self.bufsize)
                            if data:
                                # data is a command: either GET or POST
                                msg = self.process_data(sock, data)
                                self.send(sock, msg)
                            else:
                                self.sockets.remove(sock)
                                msg = 'Client {0} is offline\n'.format(sock.getpeername())
                                print(msg)
                        except Exception as error:
                            self.sockets.remove(sock)
                            print(str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
                            raise
        except KeyboardInterrupt:
            self.sock.close()


    def process_data(self, sock, data):
        command, *options = shlex.split(data.decode('utf-8'))
        namespace = parser.parse_args(options)
        if command.lower() not in ['get', 'post']:
            msg = 'Unrecognized command `{comm}`'.format(comm=command)
        elif command.lower()=='get':
            name = namespace.name
            msg = self.database_adapter.get_service_by_name(name)
        else:
            name = namespace.name
            desc = namespace.desc
            host, port = sock.getpeername()
            service = Service(host=str(host), port=int(port), name=name, description=desc)
            _repr = str(service)
            self.database_adapter.upsert(service)
            msg = 'Service {service} was successfully added'.format(service=_repr)
        return msg.strip() + os.linesep


    def send(self, sock, msg = ''):
        try:
            # '\r' is needed to owerwrite the last line (for example in progress bars)
            sock.send(bytes('\r'+msg, 'utf-8'))
        except:
            print('Broken socket - ' + str(type(error).__name__ + ' : ' + ' '.join(error.args)), file = sys.stderr, flush = True)
            sock.close()
            if sock in self.sockets:
                self.sockets.remove(new_socket)

if __name__=='__main__':
    name_server = NameServer()
    name_server.serve()
