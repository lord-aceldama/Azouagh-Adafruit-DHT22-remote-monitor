import time
import select
import socket
import argparse
from typing import Optional
from datetime import datetime as DateTime

try:
    import Adafruit_DHT
except ImportError:
    print("WARN> using dummy driver. If you want to use an actual Adafruit DHT device, please install the pip.")
    import ada_dht as Adafruit_DHT

# Sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

# Server
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 60606


def poll_sensor() -> bytes:
    """ Poll the sensor """
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    result = ""
    if None not in [humidity, temperature]:
        result = f"OK, {DateTime.now().strftime('%H:%M:%S')}, T:{temperature:0.1f}C, RH:{humidity:0.1f}%"
    else:
        result = "FAIL, Sensor failure. Check wiring."

    return bytes(result, "utf-8")


def run(port: int):
    """ Start the web server and listen on the given port. """

    print(f"Starting server on '{DEFAULT_HOST}' listening on port {port}...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((DEFAULT_HOST, port))
    server.listen(5)
    inputs = [server]

    while inputs:
        r, w, fail = select.select(inputs, inputs, inputs)

        # Handle RX
        s: Optional[socket.socket] = None
        for s in r:
            if s is server:
                # Incoming connection
                connection: Optional[socket.socket] = None
                connection, client_address = s.accept()
                print(f"NOTE> Connected to '{client_address}'.")
                connection.setblocking(False)
                inputs.append(connection)
                connection.sendall(bytes("OK, Hello", "utf-8"))
            else:
                # Incoming transmission
                try:
                    data: bytes = s.recv((2 ** 10) * 10)
                    if data:
                        # Parse data
                        print(f"INFO::RX> Received {len(data)} bytes of data")
                        ds = data.decode('utf-8')
                        print(f"INFO::RX> Data('{ds}')")

                        # Transmit sensor reading
                        sd = poll_sensor()
                        print(f"INFO::TX> Data('{sd.decode('utf-8')}')")
                        s.sendall(sd)
                except:
                    # Null data
                    print(f"INFO> Remote connection closed.")
                    inputs.remove(s)
                    s.close()
        time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help="The port to listen on. (default: %(default)s)"
    )
    args = parser.parse_args()

    run(args.port)
