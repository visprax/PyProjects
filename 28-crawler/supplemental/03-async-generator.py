#!/usr/bin/env python3

"""A simple example case of using async generators."""

import asyncio

async def something(a):
    return a*2

async def something_else(a):
    return a**2


async def agen(y):
    for i in range(0, 5):
        x = await something(y) # x times 2
        y = yield x

async def main():
    ag = agen(1)
    x = await anext(ag)
    print(f"yield of x: {x}")

    while True:
        y = await something_else(x) # x to the power of 2
        try:
            x = await ag.asend(y)
            print(f"yield of x: {x}")
        except StopAsyncIteration:
            break

if __name__ == "__main__":
    asyncio.run(main())
        
    
