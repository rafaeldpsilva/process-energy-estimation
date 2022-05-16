from powerlog import get_process_report
from threading import Thread
import psutil
import os
import pandas as pd
import numpy as np
import time
import datetime
import time

#Utils
def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def read_csv(name):
    data = pd.read_csv (name)  
    df = pd.DataFrame(data)
    df1 = df[:-14]
    return df1

def read_txt(name):
    time = []
    process_percentage = []
    with open(name) as f:
        lines = f.readlines()
        
    for line in lines:
        split = line.split()
        time.append(split[0])
        process_percentage.append(split[1])
    
    
    return [time, process_percentage]

def to_microsecs(string):
    hours = int(string[0:2]) * 3600000000
    minutes = int(string[3:5]) * 60000000 
    seconds = int(string[6:8]) * 1000000
    microseconds = int(string [9:12] +  "00") + hours + minutes + seconds
    return microseconds

def join_data():
    data = read_csv('reports/process_v2.csv')
    process_data = read_txt('reports/report.txt')

    array = []
    for line in data['System Time']:
        t2 = to_microsecs(line)
        array.append(t2)

    length = len(process_data[0])
    i = 0
    while i < length:
        t1 = to_microsecs(process_data[0][i])
        idx = find_nearest(array,t1)
        i += 1
        
    """ process_data = {'Time(sec)':time, 'Process Percentage (%)':process_percentage}
    df = pd.DataFrame(process_data) """

    

def process_usage(pid):
    while pid == 0:
        if os.path.exists('reports/pid.txt'):
            with open('reports/pid.txt') as f:
                p = f.readline()
                pid = int(p)
    
    process = psutil.Process(pid=pid)
    while True:
        try:
            f = open("reports/report.txt", "a")
            f.write(datetime.datetime.now().strftime("%H:%M:%S:%f")+ " " + str(process.cpu_percent(interval=0.1))+"\n")
            f.close()
        except:
            os.remove("reports/pid.txt")
            return 0

def evaluate(command):
    get_process_report("process_v2",command)

def main():
    """ os.remove("reports/process_v2.csv")
    f = open("reports/report.txt", "w")
    f.close()

    thread = Thread(target = process_usage, args = (0, ))
    thread.start()
    
    evaluate('"python sorting_algorithms.py"')
    
    thread.join() """
  
    join_data()


if __name__ == '__main__':
   main()