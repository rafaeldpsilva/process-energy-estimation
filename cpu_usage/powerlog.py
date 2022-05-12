import subprocess

def get_base_report(duration):
    subprocess.call('echo BaseReport & "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/base.csv -duration '+ str(duration), shell=True)

def get_process_report(file_name,command):
    subprocess.call('echo ProcessReport & "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -file ./reports/' + file_name + '.csv -cmd ' + command, shell=True)