import psutil
import subprocess
import asyncio

cpu_percent = 0

async def power_log():
    subprocess.call('\& "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -duration 3 ', shell=True)
    return 0

async def process_usage(process):
    global cpu_percent
    cpu_percent = process.cpu_percent(interval=3)
    return cpu_percent

async def main():
    # Iterate over all running processes
    for proc in psutil.process_iter():
        if( proc.name() == "stremio.exe"):
            process = psutil.Process(pid=proc.pid)
            with process.oneshot():
                name = process.name()

                f1 = loop.create_task(power_log())
                f2 = loop.create_task(process_usage(process))
                await asyncio.wait([f1, f2])
                
                
                pid = process.pid

            print("{name="+ name+ " pid="+ str(pid)+ " cpu_percent=" + str(cpu_percent) + "}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()