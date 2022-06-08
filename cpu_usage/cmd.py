import subprocess
import psutil

def get_base_report(duration):
    subprocess.run('echo BaseReport & "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/base.csv -duration '+ str(duration), shell=True)

def get_powerlog_report(filename,command):
    subprocess.run('echo ProcessReport & "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/' + filename + '.csv -cmd ' + command, shell=True)

def get_gpu_report(filename,interval):
    proc = subprocess.Popen('nvidia-smi --query-gpu=index,timestamp,power.draw --format=csv -lms ' + str(interval) + ' >> ./reports/' + filename + '.csv', shell=True)
    return proc.pid

def kill_process(pid):
    process = psutil.Process(pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()