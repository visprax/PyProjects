#!/usr/bin/env python3

"""A simple example of blocking calls with sockets."""

import time
import socket

start = time.perf_counter()

sock = socket.socket()

request = b"HEAD / HTTP/1.0\r\nHOST: github.com\r\n\r\n"

sock.connect(("github.com", 80))

sock.sendall(request)

response = sock.recv(1024)

end = time.perf_counter()

print(response.decode())

print(f"The application ran in: {end-start:0.2f}s")


