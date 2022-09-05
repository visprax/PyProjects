## Web Crawler 

This is a web crawler with `asyncio` coroutines [^1]. As opposed to traditional optimization problem of 
running an algorithm as fast as possible, optimizing a network program involvs efficiently waiting 
for infreqent network events over slow connections, this is where `asynchronous I/O` comes into play.

An example from a [PyCon talk](https://youtu.be/iG6fr81xHKA?t=4m29s) to understand the idea behind async I/O:

> Chess master Judit Polgár hosts a chess exhibition in which she plays multiple amateur players. 
    She has two ways of conducting the exhibition: synchronously and asynchronously.\
    Assumptions:\
    24 opponents\
    Judit makes each chess move in 5 seconds\
    Opponents each take 55 seconds to make a move\
    Games average 30 pair-moves (60 moves total)\
    **Synchronous version**: Judit plays one game at a time, never two at the same time, 
    until the game is complete. Each game takes (55 + 5) * 30 == 1800 seconds, or 30 minutes. 
    The entire exhibition takes 24 * 30 == 720 minutes, or **12 hours**.\
    **Asynchronous version**: Judit moves from table to table, making one move at each table. 
    She leaves the table and lets the opponent make their next move during the wait time. 
    One move on all 24 games takes Judit 24 * 5 == 120 seconds, or 2 minutes. 
    The entire exhibition is now cut down to 120 * 30 == 3600 seconds, or just **1 hour**.

We can implement the crawler using *threads* but creating thousands of threads will be expensive, and 
operating systems have mechanisms to control the cap thread a process can create.

*Asynchronous I/O* platforms will perform concurrent operations on a single thread using *non-blocking*
sockets. We set the sockets to non-blocking before connecting to the server:

```Python
s = socket.socket()
s.setblocking(False)
try:
    s.connect(("github.com", 80))
except BlockingIOError:
    pass
```

due to the underlying C function behaviour of non-blocking socket, it will throw an exception to tell
that it has begun, more details here: [Stack overflow question](https://stackoverflow.com/questions/11647046/non-blocking-socket-error-is-always)\
We need a way to know when the connection is established to send the HTTP request, we can do it a tight loop, 
but it's not an efficient way to await events on multiple sockets. The solution to this a `select` function 
in C for Unix-like machines that waits for an event to occur on muliple non-blocking sockets. Each system 
has its own replacements for it, like `epoll` on linux. Python's `selectors` module provides `DefaultSelector`
that uses the best `select` counterpart on the underlying OS.\
On may Manjaro machine:

```Python
from selectors import DefaultSelector

selector = DefaultSelector()

print(selector)
```
Output:

`<selectors.EpollSelector object at 0x7fd1501a6830>`

To register for notifications about network I/O, we create a non-blocking socket and register it with 
the default selector:

```Python
import socket
from selectors import DefaultSelector, EVENT_WRITE

selector = DefaultSelector()

s = socket.socket()
s.setblocking(False)

try:
    s.connect(("github.com", 80))
except BlockingIOError:
    pass

selector.register(s.fileno(), EVENT_WRITE, connected)

def connected():
    selector.unregister(s.fileno())
    print("connected!")
```

We register the socket with its file descriptor, and to be notified when the socket is writable, 
we pass a `EVERNT_WRITE` to wait for such an event, and we pass a callback function, `connected` 
to run when such an event occurs.

As the selector receives I/O notifications, we process them in a loop:

```Python
def loop():
    while True:
        # Here the call to select() pauses, awaiting the next
        # I/O events. Then we run callbacks that are waiting for
        # these events. Operations that have not completed remain
        # pending until some future tick of the event loop.
        events = selector.select()
        for event_key, event_mask in events:
            # event_key.data stores the `connected` callblack
            callback = event_key.data
            callback()
```
Note that here we don't have a traditional parallelism, and it's certainly not a multithreaded application, 
but it does overlapping I/O. Here we have an I/O-bound problem, and usually a multithreaded application would 
be write for these problems, though we chose not use threads because of the expensive overhead of threads at 
scale, as explained in the introduction. For applications with many slow or sleepy connections with infrequent 
events, asynchronous I/O is a right solution.



[^1]: This project is partly influenced from: [aosabook/500lines](https://github.com/aosabook/500lines/tree/master/crawler)
