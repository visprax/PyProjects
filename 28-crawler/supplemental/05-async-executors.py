#!/usr/bin/env python3

"""A simple demonstration example for using Process and Threads pools for blocking tasks."""

import asyncio
import concurrent.futures

def blocking_io():
    # File operations (e.g. logging, reading) can block event loop,
    # a thread pool can deal with blocking IO
    with open("/dev/urandom", "rb") as f:
        return f.read(100)

def cpu_bound():
    # A CPU-bound operation that will block the event loop,
    # a process pool is preferred to run  CPU-bound operations
    return sum(i * i for i in range(10**7))

async def main():
    loop = asyncio.get_running_loop()
    
    # A custom thread pool for IO-bound problem
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, blocking_io)
        print(f"Result of `blocking_io` in custom thread pool: {result}")
    
    # A custom process pool for CPU-bound problem
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, cpu_bound)
        print(f"Result of `cpu_bound` in custom process pool: {result}")

if __name__ == "__main__":
    asyncio.run(main())
