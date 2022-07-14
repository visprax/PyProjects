#!/usr/bin/env python3

""" The client program for chatroom application using socket programming."""

import socket

# the server's hostname or IP address
HOST = "0.0.0.0"
# the port used by server
PORT = 6000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello world!")
    data = s.recv(1024)

print("Received: {}".format(data))
