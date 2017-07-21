from socket import *


class UDPServer(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(self.addr)

    def serve(self):
        try:
            while True:
                data, addr = self.sock.recvfrom(self.bufsize)
                self.sock.sendto(bytes('[%s]' % (data.decode('utf-8')), 'utf-8'), addr)
                print('...received from and returned to: {0}'.format(addr))
        except KeyboardInterrupt:
            print('Socket is shutting down..')
            self.sock.close()

if __name__=='__main__':
    server = UDPServer()
    server.serve()
