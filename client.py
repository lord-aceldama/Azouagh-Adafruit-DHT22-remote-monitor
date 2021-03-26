import select
import time
import socket
import argparse

from datetime import datetime as DateTime


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 60606  # The port used by the server


def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            s.sendall(b'send anything')
            data = s.recv(1024)
            print('Received', repr(data))

            time.sleep(5)


if __name__ == '__main__':
    run()
