import subprocess
import psutil
import os
from time import sleep
def get_cpu_base_report(filename, duration):
    """Executes the PowerLog3.0 tool for the time specified and creates a csv file wi
    th the data generated during that time."""

    subprocess.run('echo BaseReport & "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe"  -file ' + filename + ' -duration '+ str(duration), shell=True)

def get_gpu_base_report(filename,interval,duration):
    """Executes the nvidia-smi command that registers the index, timestamp and power.
    draw of the gpu during the time this tool is executing. The interval in which the
    data is registered needs to be specified. The output of the command is saved in a
    specified file. This function also returns the pid of the running command."""

    proc = subprocess.Popen('nvidia-smi --query-gpu=index,timestamp,power.draw --format=csv -lms ' + str(interval) + ' >> ' + filename, shell=True)
    sleep(duration)
    kill_process(proc.pid)

def get_powerlog_report(filename,command):
    """Executes the PowerLog3.0 tool for the time that the command specified is runni
    ng and creates a csv file with the data generated during that time."""

    subprocess.run('echo ProcessReport & "C:/Program Files/Intel/Power Gadget 3.6/PowerLog3.0.exe" -file ' + filename + ' -cmd ' + command, shell=True)

def get_gpu_report(filename,interval):
    """Executes the nvidia-smi command that registers the index, timestamp and power.
    draw of the gpu during the time this tool is executing. The interval in which the
    data is registered needs to be specified. The output of the command is saved in a
    specified file. This function also returns the pid of the running command."""

    proc = subprocess.Popen('nvidia-smi --query-gpu=index,timestamp,power.draw --format=csv -lms ' + str(interval) + ' >> ' + filename, shell=True)
    return proc.pid

def run_command(command,pipe):
    "Executes a given command"

    proc = subprocess.Popen(command, shell=True)
    pipe.send(proc.pid)
    pipe.close()

def kill_process(pid):
    """Kills the process with the given pid."""
    process = psutil.Process(pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()