import time
import socket
import argparse


DEFAULT_HOST = '127.0.0.1'  # The server's hostname or IP address
DEFAULT_PORT = 60606  # The port used by the server


def run(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            # You can send literally anything and you'll get the data as a reply
            s.sendall(b"ping")
            data = s.recv(1024)
            print('Received:', data.decode("utf-8"))

            time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host", default=DEFAULT_HOST,
        help="The remote hostname/ip to connect to. (default: '%(default)s')"
    )
    parser.add_argument(
        "port", type=int, default=DEFAULT_PORT,
        help="The remote port to connect to. (default: '%(default)s')"
    )
    args = parser.parse_args()

    run(args.host, args.port)
