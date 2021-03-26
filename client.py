import time
import socket
import argparse


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
    parser.add_argument("host", help="The remote hostname/ip to connect to.")
    parser.add_argument(
        "-p", "--port", required=False, type=int, default=DEFAULT_PORT,
        help="The remote port to connect to. (default: %(default)s)"
    )
    #args = parser.parse_args()
    args = parser.parse_args(["192.168.1.5"])

    run(args.host, args.port)
