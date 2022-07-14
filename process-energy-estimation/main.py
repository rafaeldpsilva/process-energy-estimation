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

def process_cpu_usage(process_filename, pid):
    """Registers the cpu usage of the process with given pid on the specified file."""

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
    f.write("Time,Process CPU Usage(%),Total CPU Usage(%)\n")
    f.close()
    while True:
        try:
            total_cpu_usage = psutil.cpu_percent(interval=0.1)
            process_cpu_usage = process.cpu_percent(interval=None)/cpu_count
            if(process_cpu_usage != 0.0):
                f = open(process_filename, "a")
                f.write(datetime.datetime.now().strftime("%H:%M:%S:%f") + "," + str(process_cpu_usage) + "," + str(total_cpu_usage) + "\n")
                f.close()
        except:
            return 0

def join_process_data(powerlog_filename, process_filename, nvidia_smi_filename, cpu_sockets):
    """Merges the three csv files on a pandas dataframe."""

    powerlog_data = read_powerlog_file(powerlog_filename, cpu_sockets)
    process_data = read_csv_file(process_filename)
    gpu_data = read_csv_file(nvidia_smi_filename)
    gpu_data.columns = ['index','timestamp','power.draw [W]']
    cpu_time_in_microseconds = array_to_microseconds(process_data['Time'],time_to_microsecs)
    gpu_time_in_microseconds = array_to_microseconds(gpu_data['timestamp'],datatime_to_microsecs)
    cpu_df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)', 'Total CPU Usage(%)'])
    gpu_df = pd.DataFrame([], columns =['timestamp'])

    power_draw = []
    length = len(powerlog_data['System Time'])
    i = 0
    while i < length:
        time = time_to_microsecs(powerlog_data['System Time'].iloc[i])
        [cpu_idx,value] = find_nearest(cpu_time_in_microseconds,time)
        [gpu_idx,value_gpu] = find_nearest(gpu_time_in_microseconds,time)
        cpu_df = pd.concat([cpu_df,process_data.iloc[[cpu_idx],[0,1]]], ignore_index = True, axis = 0)
        
        p = gpu_data['power.draw [W]'].iloc[gpu_idx][:-2]
        power_draw.append(float(p.strip()))

        gpu_df = pd.concat([gpu_df,gpu_data.iloc[[gpu_idx],[1]]], ignore_index = True, axis = 0)
        
        i += 1
    
    df = pd.DataFrame(powerlog_data, columns=['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)','Processor Power_1(Watt)','DRAM Power_0(Watt)','Cumulative DRAM Energy_0(Joules)'])
    df = pd.concat([df, cpu_df], axis = 1)
    power_draw_df = pd.DataFrame(power_draw, columns =['power.draw [W]'])
    gpu_df = pd.concat([gpu_df, power_draw_df], axis = 1)
    #gpu_df.to_csv('process-energy-estimation/reports/gpu.csv')
    return pd.concat([df, gpu_df], axis = 1)    

def estimate_cpu_power_consumption(df):
    """Estimates the average cpu power consumption of the process by multiplying 
    the cpu usage of the process by the total cpu power consumption. It uses the 
    dataframe returned by join_process_data function so the rows from the cpu pr
    ocess usage matches the right cpu total power consumption rows. This functio
    n also returns a new dataframe with the same information present in the give
    n dataframe and an added column with the cpu process power consumption at a 
    given moment."""

    cpu_wattage_sum = 0
    i = 0
    process_power = []

    length = len(df['Time'])
    while i < length:
        cpu_power_0 = float(df['Processor Power_0(Watt)'].iloc[i])
        cpu_power_1 = float(df['Processor Power_1(Watt)'].iloc[i])
        cpu_utilization = float(df[' CPU Utilization(%)'].iloc[i])
        process_utilization = float(df['Process CPU Usage(%)'].iloc[i])

        print("cpu_power_0: "+str(cpu_power_0)+" | cpu_utilization: "+str(cpu_utilization)+" | process_utilization: "+str(process_utilization))
        power = round(process_utilization/cpu_utilization * (cpu_power_0 + cpu_power_1), 4)
        process_power.append(power)
        cpu_wattage_sum += power
        i += 1
    
    average_cpu_wattage = cpu_wattage_sum/i

    process_cpu_power_df = pd.DataFrame(process_power, columns=['Process CPU Power(Watt)'])
    df1 = pd.concat([df,process_cpu_power_df], axis = 1)
    
    return [average_cpu_wattage, df1]

def estimate_gpu_power_consumption(nvidia_smi_filename):
    """Estimates the average gpu total power consumption. This function uses the 
    file created by nvidia-smi to have the best accuracy."""

    gpu_df = read_nvidia_smi_file(nvidia_smi_filename)

    gpu_wattage_sum = 0
    i = 0
    gpu_process_power = []

    #Estimar energia da gpu
    length = len(gpu_df['power.draw [W]'])
    while i < length:
        gpu_power = float(gpu_df['power.draw [W]'].iloc[i])
        gpu_process_power.append(gpu_power)
        gpu_wattage_sum += gpu_power
        i += 1
    
    average_gpu_wattage = gpu_wattage_sum/i
    
    return average_gpu_wattage

def estimate_dram_power_consumption(df):
    """Estimates the average gpu total power consumption. This function uses the 
    file created by nvidia-smi to have the best accuracy. It returns the average
    dram power consumption and the sum of the energy consumed during the executi
    on time"""

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
    cumulative_dram_energy = df['Cumulative DRAM Energy_0(Joules)'].iloc[-1]
    return [average_dram_wattage,cumulative_dram_energy]

def main():
    [command,powerlog_filename,process_filename,nvidia_smi_filename,total_process_data,interval,cpu_sockets] = get_configuration()

    initialize_files(powerlog_filename, process_filename, nvidia_smi_filename)

    thread_cpu = Process(target = process_cpu_usage, args = (process_filename, 0, ))
    thread_cpu.start()

    pid = cmd.get_gpu_report(nvidia_smi_filename, interval)

    cmd.get_powerlog_report(powerlog_filename, command)
    
    thread_cpu.join()

    cmd.kill_process(pid)
    
    process_df = join_process_data(powerlog_filename, process_filename, nvidia_smi_filename, cpu_sockets)
    
    mean_cpu_consumption = 0
    if(get_cpu_on()):
        [mean_cpu_consumption,process_df] = estimate_cpu_power_consumption(process_df)
    
    mean_gpu_consumption = 0
    if(get_gpu_on()):
        mean_gpu_consumption = estimate_gpu_power_consumption(nvidia_smi_filename)
    
    mean_dram_consumption = 0
    dram_energy = 0
    if(get_dram_on()):
        [mean_dram_consumption,dram_energy] = estimate_dram_power_consumption(process_df)
    
    elapsed_time = process_df['Elapsed Time (sec)'].iloc[-1]
    
    print_results(elapsed_time,mean_cpu_consumption,mean_gpu_consumption,mean_dram_consumption,dram_energy)
    
    process_df.to_csv(total_process_data)

if __name__ == '__main__':
    main()