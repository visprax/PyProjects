#!/usr/bin/env python3

"""An asynchronous client that connects to the server and sends some data."""

import socket
import asyncio

# -> deprecated
loop = asyncio.get_event_loop()

async def client():
    client = socket.socket()
    client.setblocking(False)
    
    # "await" to stablish a connection
    await loop.sock_connect(client, ("localhost", 6789))
    
    message = b"Hello there server!"
    print(f"sending: {message}")

    # "await" to send the message
    await loop.sock_sendall(client, message)

    # "await" to receive a reponse
    response = await loop.sock_recv(client, 1024)

    print(f"received: {response}")

    client.close()


if __name__ == "__main__":
    # -> deprecated
    loop.run_until_complete(client())
    # asyncio.run(client())

