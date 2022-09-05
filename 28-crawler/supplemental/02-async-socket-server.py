#!/usr/bin/env python3

"""An asynchronous server that responds with the reverse of the request."""

import socket
import asyncio

# get the default event loop that we will run -> deprecated
loop = asyncio.get_event_loop() 

async def server():
    server = socket.socket()
    server.setblocking(False)
    server.bind(("localhost", 6789))
    server.listen(1)

    # sock_accept is async version of socket.accept(),
    # the event loop can run other code, while the 
    # socket accepts connections
    client, _ = await loop.sock_accept(server)

    # "await" for some data
    data = await loop.sock_recv(client, 1024)
    data = data[::-1]

    # "await" for sending the data
    await loop.sock_sendall(client, data)

    client.close()
    server.close()

if __name__ == "__main__":
    # run the loop until the server coroutine is complete -> deprecated
    loop.run_until_complete(server())
    # asyncio.run(server())
