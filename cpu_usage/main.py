from multiprocessing import Process, Semaphore
from utils import *
import cmd
import threading
import psutil
import subprocess, os, signal
import pandas as pd
import time
import datetime

powerlog_filename = 'reports/process.csv'
process_filename = 'reports/report.txt'
nvidia_smi_filename = 'reports/nvidia.csv'
pid_filename = 'reports/pid.txt'

def process_cpu_usage(pid):

    #TODO transformar a comunicação de ficheiros em comunicação em pipes

    while pid == 0:
        if os.path.exists(pid_filename):
            with open(pid_filename) as f:
                p = f.readline()
                pid = int(p)
    
    process = psutil.Process(pid=pid)
    while True:
        try:
            f = open(process_filename, "a")
            f.write(datetime.datetime.now().strftime("%H:%M:%S:%f")+ " " + str(process.cpu_percent(interval=0.05))+"\n")
            f.close()
        except:
            os.remove(pid_filename)
            return 0

def join_process_data():
    powerlog_data = read_csv(powerlog_filename)
    process_data = read_txt(process_filename)

    system_time_in_microseconds = array_to_microseconds(powerlog_data['System Time'])

    df = pd.DataFrame([], columns =['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)'])

    length = len(process_data['Time'])
    i = 0
    SYSTEM_TIME = 0
    ELAPSED_TIME = 2
    CPU_UTILIZATION = 3
    PROCESSOR_POWER = 5

    while i < length:
        time = time_to_microsecs(process_data['Time'].iloc[i])
        [idx,value] = find_nearest(system_time_in_microseconds,time)
        #TODO trocar powerlog_data para process_data
        df = pd.concat([df,powerlog_data.iloc[[idx],[SYSTEM_TIME,ELAPSED_TIME,CPU_UTILIZATION,PROCESSOR_POWER]]], ignore_index = True, axis = 0)
        i += 1
    
    cpu_df = pd.DataFrame(process_data, columns=['Time', 'Process CPU Usage(%)'])
    return pd.concat([df,cpu_df], axis = 1)

def join_gpu_data(powerlog_data):
    gpu_data = read_csv(nvidia_smi_filename)
    
    system_time_in_microseconds = array_to_microseconds(powerlog_data['System Time'])

    data = pd.DataFrame([], columns =['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)', 'Time', 'Process CPU Usage(%)'])

    SYSTEM_TIME = 0
    ELAPSED_TIME = 1
    CPU_UTILIZATION = 2
    PROCESSOR_POWER = 3
    PROCESS_TIME = 4
    PROCESS_CPU_USAGE = 5

    power_draw = []
    length = len(gpu_data[' timestamp'])
    i = 0
    while i < length:
        power_draw.append(gpu_data[' power.draw [W]'].iloc[i][:-2]) #remove "W" character

        time = datatime_to_microsecs(gpu_data[' timestamp'].iloc[i])
        [idx,value] = find_nearest(system_time_in_microseconds,time)
        #TODO trocar powerlog_data para gpu_data
        data = pd.concat([data,powerlog_data.iloc[[idx],[SYSTEM_TIME,ELAPSED_TIME,CPU_UTILIZATION,PROCESSOR_POWER,PROCESS_TIME,PROCESS_CPU_USAGE]]], ignore_index = True, axis = 0)
        i += 1
    
    gpu_df = pd.DataFrame(gpu_data, columns=[' timestamp'])
    gpu_df['power.draw [W]'] = power_draw
    return pd.concat([data,gpu_df], axis = 1)

def estimate_process_power_consumption(df):
    cpu_wattage_sum = 0
    i = 0
    process_power = []

    #Estimar energia do cpu
    length = len(df['Time'])
    while i < length:
        cpu_power = float(df['Processor Power_0(Watt)'].iloc[i])
        cpu_utilization = float(df[' CPU Utilization(%)'].iloc[i])
        process_utilization = float(df['Process CPU Usage(%)'].iloc[i])
        power = round(process_utilization/100 * cpu_power, 4)
        process_power.append(power)
        cpu_wattage_sum += power
        i += 1
    
    average_cpu_wattage = cpu_wattage_sum/i

    process_cpu_power_df = pd.DataFrame(process_power, columns=['Process CPU Power(Watt)'])
    df1 = pd.concat([df,process_cpu_power_df], axis = 1)
    
    return [average_cpu_wattage, df1]

def estimate_gpu_power_consumption(df):
    gpu_wattage_sum = 0
    i = 0
    gpu_process_power = []

    #Estimar energia do cpu
    length = len(df[' timestamp'])
    while i < length:
        gpu_power = float(df['power.draw [W]'].iloc[i])
        gpu_process_power.append(gpu_power)
        gpu_wattage_sum += gpu_power
        i += 1
    
    average_gpu_wattage = gpu_wattage_sum/i
    
    return average_gpu_wattage

def estimate_dram_power_consumption(df):
    gpu_wattage_sum = 0
    i = 0
    gpu_process_power = []

    #Estimar energia do cpu
    length = len(df[' timestamp'])
    while i < length:
        gpu_power = float(df['power.draw [W]'].iloc[i])
        gpu_process_power.append(gpu_power)
        gpu_wattage_sum += gpu_power
        i += 1
    
    average_gpu_wattage = gpu_wattage_sum/i
    
    return average_gpu_wattage

def main():
    """ initialize_files(powerlog_filename, process_filename, nvidia_smi_filename, pid_filename)

    thread_cpu = Process(target = process_cpu_usage, args = (0, ))
    thread_cpu.start()

    pid = cmd.get_gpu_report("nvidia", 100)
    cmd.get_powerlog_report("process",'"python sorting_algorithms.py"')
    
    thread_cpu.join()

    cmd.kill_process(pid) """

    process_df = join_process_data()
    gpu_process_df = join_gpu_data(process_df)

    [cpu_consumption,gpu_process_df] = estimate_process_power_consumption(gpu_process_df)
    gpu_consumption = estimate_gpu_power_consumption(gpu_process_df)
    dram_consumption = estimate_dram_power_consumption(gpu_process_df)

    elapsed_time = gpu_process_df['Elapsed Time (sec)'].iloc[-1]
    
    total_consumption = cpu_consumption + gpu_consumption + dram_consumption
    print_results(elapsed_time,total_consumption)
    
    gpu_process_df.to_csv('reports/n.csv')

if __name__ == '__main__':
    main()