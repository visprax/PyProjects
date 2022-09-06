#!/usr/bin/env python

"""Count from 0 to 5 using async tasks."""

import asyncio

async def count(task_name):
    for i in range(0, 6):
        print(f"{task_name}: {i}")
        await asyncio.sleep(0)

async def main():
    tasks = []
    # 4 tasks
    for i in range(0, 4):
        tasks.append(asyncio.create_task(count(f"Task {i}")))

    while True:
        tasks = [task for task in tasks if not task.done()]
        if len(tasks) == 0:
            return

        await tasks[0]


if __name__ == "__main__":
    asyncio.run(main())
