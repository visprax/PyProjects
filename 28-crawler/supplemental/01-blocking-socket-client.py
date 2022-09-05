#!/usr/bin/env python3

"""A simple client with blocking sockets.
    The client connects to server and sends data and receives response."""

import socket

def client():
    client = socket.socket()

    # blockingly try to establish a connection
    client.connect(("localhost", 6789))

    message = b"Hello there server!\n"
    print(f"sending: {message}")
    # blockingly try to send the message
    client.sendall(message)

    # block until client receives a response
    response = client.recv(1024)
    print(f"received: {response}")

    client.close()

if __name__ == "__main__":
    client()
