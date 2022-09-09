## Web Crawler 

This is a web crawler with `asyncio` coroutines [^1]. As opposed to traditional optimization problem of 
running an algorithm as fast as possible, optimizing a network program involves efficiently waiting 
for infrequent network events over slow connections, this is where **asynchronous I/O** comes into play.

### Asynchronous programming
There are two main ways to perform I/O operations, such as reading or writing from a file or a network socket [^2].\
The first one is known as *blocking I/O*. When you're performing I/O, the current application thread is going 
to block the control flow until operating system can tell you it's done, this can be a performance bottleneck:

```Python
import socket

# By default sockets are open in blocking mode.
sock = socket.socket()
request = b"HEAD / HTTP/1.0\r\nHost: github.com\r\n\r\n"

# `connect` will block until a successful TCP 
# connection is made to the host on the port.
sock.connect(("github.com", 80))

# `sendall` will repeatedly call `send` until all the data in 
# `request` is sent to the host, it blocks until the data is sent.
sock.sendall(request)

# `recv` will try to receive up to 1024 bytes from the host, and block 
# until there all data is received or the host closes the connection.
response = sock.recv(1024)

# Finally, after all the blocking calls, we have received all the data,
# which are the headers from making a HTTP request to the host.
print(response.decode())
```

Blocking I/O has a timeout that after if the operation is not finished, it will give back the control.
Suppose that we can make the timeout smaller and smaller, if sufficiently small, the call will never be
blocking, that's how the asynchronous I/O works. If the I/O device needs a while to respond with proper 
data, the OS responds with "not ready", and the application gets control again, the application can check
repeatedly to see if the OS is ready to give the necessary data, but in reality the application can tell 
the OS to notify when it's ready, as opposed to *polling* (constantly asking the OS whether the data is 
ready yet or not).

`asyncio`'s *event loop* is responsible for handling those I/O events. (e.g. File is ready, data arrived, 
flushing is done, ...), event loop can decide to continue with the application while a server is trying to 
send a respond to a previous non-blocking request, whenever the data arrived, it can continue with the part
of the application that deals with that data, the `await` keyword is used to tell the event loop that at this 
point in the application, we can continue on without blocking the control flow.\
Consider this pseudo-code for the order of executing a method asynchronously:

```
async def method(request):
    prepare request
    
    await send request

    await receive response

    process response
    return result

run asynchronously(method(request1), method(request2))
```

This is an example of what the event loop for the above pseudo-code can look like:

```
no events pending, advance
enter method with request1
    prepare request1
    await sending request1
pause method with request1
enter method with request2
    prepare request2
    await sending request2
pause method with request2

all current non-finished methods have been puased, can't advance, wait for events

event for request2 arrives (sending request2 completed)
enter method with request2
    await receiving response2
pause method with request2

event for request1 arrives (sending request1 completed)
enter method with request1
    await receiving response1
pause method with request1

event for response1 arrives (receiving response1 completed)
enter method with request1
    process response1
    return result1
finish method with request1

all current non-finished methods have been paused, can't advance, wait for events

event for response2 arrives (receiving response2 completed)
enter method with request2
    process response2
    return result2
finish method with request2

all methods are finished, asynchronous run completed
```

To tell the `asyncio` to run the two methods shown above, we can use `asyncio.ensure_future`,
which is a way of saying to ensure the future of the methods, that you want the event loop 
to run them as soon as it's free to do so. This method returns a `Future` object, that represents 
an object that will be there, but might not be there yet. We can `await` these `Future`'s just like 
we can `await` the `async def` functions, which are also called **coroutines**.

Note that there is a subtle difference between a non-blocking call and an asynchronous one, 
a non-blocking call returns immediately, with whatever data are available, either the full number 
of bytes requested, fewer, or none at all. An asynchronous call requests a transfer that will be 
performed in its entirety, but will complete at some future time.

#### Awaitables, Tasks and Futures

Note that, if we have an example coroutine such as `async def example_coroutine(a, b)`, as opposed 
to normal functions, when we invoke the coroutine like `r = example_coroutine(1, 2)`, the control 
flow won't go inside the coroutine definition, and it will immediately return with a `Coroutine`
object. To actually make the code block to run we have to use the facilities the `asyncio` module 
provides, such as `await` keyword, or `asyncio.gather` function.

`await` keyword can only be used inside a coroutine definition (also `async for` and `async with`, more on them later), 
it is usually used in expressions such as `r = await C`, it takes a single parameter and whenever 
event loop sees it fit, it will return a value and will be assigned to r.

We say a coroutine object is *awaitable*, meaning that it can be used in an `await` statement. Many 
asyncio APIs are designed to accept awaitables. Apart from coroutines, there are two other main types 
of awaitable objects: **Tasks**, and **Futures**. Also if an object defines the special method `__await__`, 
it can be awaited upon, in which case the behaviour is defined by the method definition.

*Tasks* are used to schedule coroutines *concurrently*. When a coroutine is wrapped into a Task with 
functions like `asyncio.create_task()` the coroutine is autamtically scheduled to run as soon as possible:

```Python
import asyncio

async def simple():
    return 10

async def main():
    # schedule to run `simple()` concurrently with `main()`
    task = asyncio.create_task(simple())
    
    # task can be used now to awaited until it's complete or 
    # it can be used to cancel `simple()`
    await task

asyncio.run(main())
```

Each event loop contains a number of tasks, and every coroutine that is executing is doing so inside a task.
The `create_task` functions takes a coroutine object and returns a `Task` object, which inherits from `asyncio.Future`.
The call creates the task inside the event loop of the current thread, and starts the task by executing from the beginning 
of the coroutine code-block. The returned future will be marked `done` only when the task has finished execution. 
Creating a task is a synchronous call, it can be done anywhere, inside a synchronous or asynchronous code, however 
if it's created inside an async code, the event loop is already there, and when it gets the next opportunity, it 
might make the new task active.

Note that due to the asynchronous code execution model, the traditional multi-threaded code problems of data races where 
different threads alter the same variable are severely reduced in async code (but not entirely eliminated), in particular 
all the synchronous code that perform operations on a data shared between tasks on the same event loop, can be considered 
*atomic* operations.\
Consider this example:

```Python
import asyncio

# Global values list
vals = []

async def get_from_io():
    # Some I/O heavy code that returns a list of values
    pass

async def fetch():
    while True:
        io_vals = await get_from_io()
        for val in io_vals:
            vals.append(val)

async def monitor():
    while True:
        print(len(vals))
        await asyncio.sleep(1)

async def main():
    task1 = asyncio.create_task(fetch())
    task2 = asyncio.create_task(monitor())
    # Note that instead of explicitely creating tasks, 
    # we could have done `asyncio.gather(fetch(), monitor())`
    await asyncio.gather(task1, task2)

asyncio.run(main())
```

Even though that the two tasks, `fetch` and `monitor` access global variable `vals`, they do so in two tasks 
that are scheduled in the same event loop, for this reason the print statement in monitor coroutine will not 
run unless fetch has appended val to vals an is inactive, and so there is no race condition between append and
print statements.

A *Future* object is another awaitable type. Unlike a coroutine object when a future is awaited it does not cause 
a block of code to be executed. It represents an *eventual* result of an asynchronous operation. When a Future is 
awaited following happens:

 * If the process the future represents has finished and returned a value then the await statement immediately returns that value.
 * If the process the future represents has finished and raised an exception then the await statement immediately raises that exception.
 * If the process the future represents has not yet finished then the current Task is paused until the process has finished. Once finished 
    it behaves as describe in above two cases.

A Future object, `f` has following synchronous API in addition to being awaitable:
 * `f.done()` returns `True` if the process has finished.
 * `f.exception()` raise an `asyncio.InvalidStateError` exception if the process has not yet finished. If the process 
    has finished it returns the exception it raised, or `None` if it terminated without raising.
 * `f.result()` raise an `asyncio.InvalidStateError` exception if the process has not yet finished. If the process
    has finished it raises the exception it raised, or returns the value it returned if it finished without raising.

A Coroutine will not be executed until it is awaited. A Future represents something that is executing anyway, ans simply allows 
to wait for it to finish, check if it has finished, or fetch the result if it has finished. A Future is a low-level awaitable, 
and usually there is no need to explicitly create one, to create one:\
 ```
f = asyncio.get_running_loop().create_future()
```

`asyncio.run(coro)` is used to run coroutine *coro* and return the result. This function runs the passed coroutine, taking 
care of managing the asyncio event loop. It will always start a new event loop, and it cannot be called when the event loop 
is already running.

There is a neat trick, if need arises and we want to interrupt the current task and *yield* the control back to the event loop 
so that other tasks may run, apart from automatically yielding control by awaiting a future returned by some call, we can do:

```Python
# Specifying a count of zero seconds works to interrupt the current task if other 
# tasks are pending, but otherwise doesn’t do anything since the sleep time is zero
await asyncio.sleep(0)
```

#### Asynchronous context managers

*Asynchronous context manager* is an extension of the synchronous context manager to work in an asynchronous environment.
`async with` is used to initiate an async context manager.\
A simple demonstration:

```Python
# Both FileProvider and fprovider.open_read return an async context manager
async with FileProvider(path) as fprovider:
    async with fprovider.open_read(config) as freader:
        # freader.read is a coroutin that returns a list of some data
        data = await freader.read(256)
        # Do other things using freader
    # Do some other things using fprovider
# Do things with data 
```
Async context manager is essentially the same as synchronous context manager, with one major difference:
 * The entry and exit from context manager is performed by awaiting asynchronous coroutines.

We can define our own asynchronous context manager by creating classes which implement the special coroutine 
methods:

```Python
# The return value could any object and it can be bound 
# by any `as` clause in `async with` statement
async def __aenter__(self):
    pass

# If the code block of `async with` reaches its end without any exceptions, `__aexit__` 
# will be called with all three parameters as `None` and its return value will be ignored.
# If it raises an exception, `__aexit__` will be called with the type of exception, 
# the exception object itself, and a traceback associated with the exception, 
# if it returns True, the system assumes the exception has been handled, and will not 
# propagate, if it returns False, the exception will continue to propagate.
async def __aexit__(self, exc_t, exc_v, exc_tb):
    pass
```

This behaviour mirrors their synchronous special methods counterparts, `__enter__` and `__exit__`.

#### Asynchronous iterators

An async iterable represents a source of data which can be looped over with an `async for` loop:

```Python
# `reader.get_quotes` returns an asynchronous iterable object
async for quote in reader.get_quotes():
    # Do something with quote
    pass
```

This is much like a normal for loop running over an iterable, the difference is that the method used 
to extract the next element from the asynchronous iterator is an asynchronous coroutine method and its
output is *awaited*.

Much like `await` and `async with`, `async for` loop can only be used in a context where asynchronous code 
is permitted (such as coroutines defined with `async def`).

To implement a custom asynchronous iterator, it must define two special methods of `__aiter__` and `__anext__`:

```Python
# Note that `__aiter__` is not a coroutine method.
# `__aiter__` must return `self`
def __aiter__(self):
    return self

# This must return the next item in the 
# iterator each time it is awaited.
async def __anext__(self):
    pass
```

#### Asynchronous generators

An async generator can be used as a shorthand method for defining an async iterator. 
For a coroutine to be considered an async generator, it must at some point `yield`.
Note that an async generator is not a coroutine and it cannot be awaited:

```Python
async def coro():
    return 3

async def agen():
    yield 3
    yield 1

# Ok
r = await coro()

# TypeError: object async_generator can't be used in 'await' expression
r = await agen()
```

However the async generator object returned from the call is an async iterator, and can be used 
in an `async for` loop:

```Python
async for r in agen():
    # will print 3 and 1
    print(r)
```

For an async generator `agen` the first time `agen.__anext__()` is awaited the execution will
continue in the generator until it reaches the first `yield` statement (or the code block ends/returns),
and the value passed to yield will be the value returned by the await. The subsequent time that `agen.__anext__()` 
is awaited the code will continue running from where it left off last time until it gets to the next yield statement.
If the execution reaches a `return` statement or the end of code block, this will cause the await of `agen.__anext__()`
to raise `StopAsyncIteration`, which will be caught by `asyn for` loop. Note that a `return` statement with value, 
inside an async generator is a syntax error.

We remember from synchronous programming that apart from yielding from generators we can also send values to them:

```Python
def times2():
    while True:
        x = yield   # (3)
        yield x * 2 # (4)

gen = times2()
next(gen)   # advance until the first yield (3)
gen.send(4) # x is now 4, yield 8  (4)
next(gen)   # go to (3)
gen.send(9) # x is now 9, yield 18 (4)
```

We can practically do the same thing in an async generator also, take this simple example case:

```Python
import asyncio

async def something(a):
    return a*2

async def something_else(a):
    return a**2

async def agen(y):
    for i in range(0, 4):
        x = await something(y)
        y = yield x

async def main():
    ag = agen(1)
    # the first advance of agen until yield, 
    # will yield 2
    x = await anex(ag)
    print(f"yield of x: {x}")

    while True:
        y = await something_else(x)
        try:
            # send y back to the agen and assign it to y
            x = await ag.asend(y)
            print(f"yield of x: {x}")
        except StopAsyncIteration:
            break

if __name__ == "__main__":
    asyncio.run(main())
    # Output:
    # yield of x: 2
    # yield of x: 8
    # yield of x: 128
    # yield of x: 32768 
```





------------------------------------------------------------------------------------------------------------
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


#### Resources

- An excellent article on *asyncio* by Lonami: [asyncio](https://lonami.dev/blog/asyncio/)
- Another good tutorial on Python *async* programming: [asyncio](https://bbc.github.io/cloudfit-public-docs/asyncio/asyncio-part-1)


[^1]: This project is partly influenced from: [aosabook/500lines](https://github.com/aosabook/500lines/tree/master/crawler)
[^2]: Lonami's article on asyncio: [asyncio](https://lonami.dev/blog/asyncio/)

