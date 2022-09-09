#!/usr/bin/env python3

"""A simple demonstration to use threads for blocking calls with async coroutines."""

import time
import asyncio
import concurrent.futures


def blocking_call(n):
    print(f"starting blocking call, param: {n}")
    time.sleep(0.1)
    print(f"blocking call done, w/  param: {n}")
    return n ** 2

async def processes_for_blockers(exector):
    print("starting threaded blockers")
    loop = asyncio.get_event_loop()

    print("creating exector tasks")
    blocking_tasks = [loop.run_in_executor(exector, blocking_call, i) for i in range(6)]

    print("awaiting executor tasks")
    completed, pending = await asyncio.wait(blocking_tasks)

    results = [task.result() for task in completed]
    print(f"results: {results}")

if __name__ == "__main__":

    exector = concurrent.futures.ProcessPoolExecutor(max_workers=4)

    asyncio.run(processes_for_blockers(exector))



