from socket import *

class UDPClient(object):

    def __init__(self, HOST = 'localhost', PORT = 2097, BUFSIZ = 1024):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.addr = (HOST, PORT)
        self.bufsize = BUFSIZ

    def communicate(self):
        try:
            while True:
                data = input('> ')
                if not data:
                    break
                self.sock.sendto(bytes(data, 'utf-8'), self.addr)
                data, addr = self.sock.recvfrom(self.bufsize)
                if not data:
                    break
                print(data.decode('utf-8'))
        except KeyboardInterrupt:
            self.sock.close()


if __name__=='__main__':
    client = UDPClient()
    client.communicate()
