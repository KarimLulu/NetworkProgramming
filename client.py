from socket import *
import sys


def main():
    HOST = 'localhost'
    PORT = 2197
    ADDR = (HOST, PORT)
    BUFSIZE = 1024

    server = socket(AF_INET, SOCK_STREAM)
    server.connect(ADDR)

    while True:
        data = input('> ')
        if not data:
            break
        server.send(bytes(data, 'utf-8'))
        data = server.recv(BUFSIZE)
        if not data:
            break
        print(data.decode('utf-8'))
    server.close()


if __name__ == '__main__':
    main()
