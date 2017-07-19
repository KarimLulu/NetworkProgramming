from socket import *
import sys


def main():
    HOST = 'localhost'
    PORT = 2197
    ADDR = (HOST, PORT)
    BUFSIZE = 1024

    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(ADDR)
    server.listen(10)

    try:
        while True:
            clientSock, addr = server.accept()
            print('Connected from {0}'.format(addr))
            while True:
                data = clientSock.recv(BUFSIZE)
                if not data:
                    break
                clientSock.send(bytes('[{0}]'.format(data.decode('utf-8')), 'utf-8'))
            clientSock.close()
    except KeyboardInterrupt:
        server.close()


if __name__ == '__main__':
    main()
