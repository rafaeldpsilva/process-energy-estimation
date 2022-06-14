from multiprocessing import Process, Semaphore
from multiprocessing.connection import Listener
from utils import *
import cmd
import threading
import psutil
import subprocess, os, signal
import pandas as pd
import time
import datetime

powerlog_filename = 'reports/process.csv'
process_filename = 'reports/report.csv'
nvidia_smi_filename = 'reports/nvidia.csv'
total_process_data = 'reports/total_process_data.csv'

def process_cpu_usage(pid):
    cpu_count = psutil.cpu_count()/2
    address = ('localhost', 6000)
    listener = Listener(address, authkey=b'secret password')
    conn = listener.accept()
    while True:
        msg = conn.recv()
        msg = int(msg)
        if isinstance(msg, int):
            pid = msg
            conn.close()
            break
    listener.close() 
    
    process = psutil.Process(pid=pid)
    f = open(process_filename, "w")
    f.write("Time,Process CPU Usage(%)\n")
    f.close()
    while True:
        try:
            usage = process.cpu_percent(interval=None)/cpu_count
            if(usage != 0.0):
                f = open(process_filename, "a")
                f.write(datetime.datetime.now().strftime("%H:%M:%S:%f")+ ", " + str(usage) +"\n")
                f.close()
        except:
            return 0

def join_process_data():
    powerlog_data = read_csv(powerlog_filename)
    process_data = read_csv(process_filename)
    gpu_data = read_csv(nvidia_smi_filename)
    gpu_data.columns = ['index','timestamp','power.draw [W]']
    cpu_time_in_microseconds = array_to_microseconds(process_data['Time'],time_to_microsecs)
    gpu_time_in_microseconds = array_to_microseconds(gpu_data['timestamp'],datatime_to_microsecs)
    cpu_df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)'])
    gpu_df = pd.DataFrame([], columns =['timestamp'])

    power_draw = []
    length = len(powerlog_data['System Time'])
    i = 0
    while i < length:
        time = time_to_microsecs(powerlog_data['System Time'].iloc[i])
        [cpu_idx,value] = find_nearest(cpu_time_in_microseconds,time)
        [gpu_idx,value_gpu] = find_nearest(gpu_time_in_microseconds,time)
        cpu_df = pd.concat([cpu_df,process_data.iloc[[cpu_idx],[0,1]]], ignore_index = True, axis = 0)
        
        power_draw.append(gpu_data['power.draw [W]'].iloc[i][:-2])

        gpu_df = pd.concat([gpu_df,gpu_data.iloc[[gpu_idx],[1]]], ignore_index = True, axis = 0)
        i += 1
    
    df = pd.DataFrame(powerlog_data, columns=['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)','DRAM Power_0(Watt)','Cumulative DRAM Energy_0(Joules)'])
    df = pd.concat([df, cpu_df], axis = 1)
    power_draw_df = pd.DataFrame(power_draw, columns =['power.draw [W]'])
    gpu_df = pd.concat([gpu_df, power_draw_df], axis = 1)
    return pd.concat([df, gpu_df], axis = 1)    

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
    length = len(df['timestamp'])
    while i < length:
        gpu_power = float(df['power.draw [W]'].iloc[i])
        gpu_process_power.append(gpu_power)
        gpu_wattage_sum += gpu_power
        i += 1
    
    average_gpu_wattage = gpu_wattage_sum/i
    
    return average_gpu_wattage

def estimate_dram_power_consumption(df):
    dram_wattage_sum = 0
    i = 0
    dram_process_power = []

    #Estimar energia do cpu
    length = len(df['System Time'])
    while i < length:
        dram_power = float(df['DRAM Power_0(Watt)'].iloc[i])
        dram_process_power.append(dram_power)
        dram_wattage_sum += dram_power
        i += 1
    
    average_dram_wattage = dram_wattage_sum/i
    
    return average_dram_wattage

def main():
    initialize_files(powerlog_filename, process_filename, nvidia_smi_filename)

    thread_cpu = Process(target = process_cpu_usage, args = (0, ))
    thread_cpu.start()

    pid = cmd.get_gpu_report("nvidia", 100)
    cmd.get_powerlog_report("process",'"python sorting_algorithms.py"')
    
    thread_cpu.join()

    cmd.kill_process(pid)
    
    process_df = join_process_data()

    [mean_cpu_consumption,process_df] = estimate_process_power_consumption(process_df)
    mean_gpu_consumption = estimate_gpu_power_consumption(process_df)
    mean_dram_consumption = estimate_dram_power_consumption(process_df)

    elapsed_time = process_df['Elapsed Time (sec)'].iloc[-1]
    
    print_results(elapsed_time,mean_cpu_consumption,mean_gpu_consumption,mean_dram_consumption)
    
    process_df.to_csv('reports/total_process_data.csv')

if __name__ == '__main__':
    main()