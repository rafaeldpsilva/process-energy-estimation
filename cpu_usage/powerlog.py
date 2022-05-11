import subprocess

def get_base_report(duration):
    subprocess.call('\& "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/base.csv -duration '+ str(duration), shell=True)

def get_process_report(command):
    subprocess.call('\& "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/process.csv -cmd '+ command, shell=True)