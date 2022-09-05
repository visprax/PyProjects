#!/usr/bin/env python3

"""A simple server with blocking sockets.
    The server responds with the reversed text a client sends."""

import socket

def server():
    # By default the socket is blocking
    server = socket.socket()
    
    # bind to localhost:6789 for new connections
    server.bind(("localhost", 6789))
    
    # listen for one client at most
    server.listen(1)

    # blockingly wait for a new client
    client, _ = server.accept()
    
    # blockingly waut for some data
    data = client.recv(1024)

    # reverse the data
    data = data[::-1]

    # blockingly send the data
    client.sendall(data)

    # close client and server
    client.close()
    server.close()

if __name__ == "__main__":
    # blockingly run the server
    server()

