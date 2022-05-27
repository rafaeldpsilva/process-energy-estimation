from powerlog import get_process_report
from threading import Thread
from utils import *
import psutil
import os
import pandas as pd
import time
import datetime

def join_data():
    total_data = read_csv('reports/process_v2.csv')
    process_data = read_txt('reports/report.txt')

    system_time_in_microseconds = []
    for line in total_data['System Time']:
        time = to_microsecs(line)
        system_time_in_microseconds.append(time)

    data = pd.DataFrame([], columns =['System Time',' CPU Utilization(%)','Processor Power_0(Watt)'])

    length = len(process_data['Time'])
    i = 0
    while i < length:
        time = to_microsecs(process_data['Time'].iloc[i])
        [idx,value] = find_nearest(system_time_in_microseconds,time)
        data = pd.concat([data,total_data.iloc[[idx],[SYSTEM_TIME,ELAPSED_TIME,CPU_UTILIZATION,PROCESSOR_POWER]]], ignore_index = True, axis = 0)
        i += 1
    
    df = pd.DataFrame(process_data, columns=['Time', 'Process CPU Usage(%)'])
    return pd.concat([data,df], axis = 1)
    
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
            f.write(datetime.datetime.now().strftime("%H:%M:%S:%f")+ " " + str(process.cpu_percent(interval=0.05))+"\n")
            f.close()
        except:
            os.remove("reports/pid.txt")
            return 0

def estimate_process_power_consumption(df):
    length = len(df['Time'])
    consumption = 0
    i = 0
    process_power = []
    while i < length:
        cpu_power = float(df['Processor Power_0(Watt)'].iloc[i])
        cpu_utilization = float(df[' CPU Utilization(%)'].iloc[i])
        process_utilization = float(df['Process CPU Usage(%)'].iloc[i])
        power = round(process_utilization/100 * cpu_power, 4)
        process_power.append(power)
        consumption += power
        i += 1
    
    process_power_df = pd.DataFrame(process_power, columns=['Process CPU Power(Watt)'])
    df1 = pd.concat([df,process_power_df], axis = 1)
    
    return [consumption, df1]

def main():
    initialize_files()

    thread = Thread(target = process_usage, args = (0, ))
    thread.start()
    get_process_report("process_v2",'"python sorting_algorithms.py"')
    thread.join()
  
    df=join_data()
    [consumption,df] = estimate_process_power_consumption(df)
    elapsed_time = df['Elapsed Time (sec)'].iloc[-1]
   
    print_results(elapsed_time,consumption)
    
    """ plot_usage() """
    
    df.to_csv('reports/n.csv')

    plot_power(df)
   


if __name__ == '__main__':
    main()