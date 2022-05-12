import psutil
import os
import asyncio
from powerlog import get_process_report

async def process_usage(pid):
    process = psutil.Process(pid=pid)
    while True:
        with process.oneshot():
            name = process.name()
            print(process)

async def evaluate(command):
    get_process_report("process_v2",command)
    return 0

async def run_evaluation():
    pid = os.getpid()
    print(pid)

    f1 = loop.create_task(evaluate('"python sorting_algorithms.py"'))
    f2 = loop.create_task(process_usage(pid))
    await asyncio.wait([f1,f2])
    f2.cancel()

#def main():
loop = asyncio.get_event_loop()
loop.run_until_complete(run_evaluation())
loop.close()

#if __name__ == '__main__':
#   main()