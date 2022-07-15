from multiprocessing import Process, Semaphore
from multiprocessing.connection import Listener
import utils
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
            process_cpu_usage = process.cpu_percent(interval=0.1)/cpu_count
            total_cpu_usage = psutil.cpu_percent(interval=None)
            if(process_cpu_usage != 0.0):
                f = open(process_filename, "a")
                f.write(datetime.datetime.now().strftime("%H:%M:%S:%f") + "," + str(process_cpu_usage) + "," + str(total_cpu_usage) + "\n")
                f.close()
        except:
            return 0

def join_process_data(powerlog_filename, process_filename, nvidia_smi_filename, cpu_sockets):
    """Merges the three csv files on a pandas dataframe."""

    powerlog_data = utils.read_powerlog_file(powerlog_filename, cpu_sockets)
    process_data = utils.read_csv_file(process_filename)
    gpu_df = utils.read_nvidia_smi_file(nvidia_smi_filename)
    cpu_time_in_microseconds = utils.array_to_microseconds(process_data['Time'],utils.time_to_microsecs)
    cpu_df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)', 'Total CPU Usage(%)'])

    power_draw = []
    length = len(powerlog_data['System Time'])
    i = 0
    while i < length:
        time = utils.time_to_microsecs(powerlog_data['System Time'].iloc[i])
        [cpu_idx,value] = utils.find_nearest(cpu_time_in_microseconds,time)
        cpu_df = pd.concat([cpu_df,process_data.iloc[[cpu_idx],[0,1]]], ignore_index = True, axis = 0)      
        i += 1
    
    df = pd.DataFrame(powerlog_data, columns=['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)','Processor Power_1(Watt)','DRAM Power_0(Watt)','Cumulative DRAM Energy_0(Joules)'])

    return pd.concat([df, cpu_df], axis = 1)

def estimate_cpu_power_consumption(df):
    """Estimates the average cpu power consumption of the process by multiplying 
    the cpu usage of the process by the total cpu power consumption. It uses the 
    dataframe returned by join_process_data function so the rows from the cpu pr
    ocess usage matches the right cpu total power consumption rows. This functio
    n also returns a new dataframe with the same information present in the give
    n dataframe and an added column with the cpu process power consumption at a 
    given moment."""

    cpu_power_sum = []
    process_power = []

    i = 0
    length = len(df['Time'])
    while i < length:
        cpu_utilization = float(df[' CPU Utilization(%)'].iloc[i])
        process_utilization = float(df['Process CPU Usage(%)'].iloc[i])
        
        power1 = 0
        cpu_sockets = utils.get_physical_cpu_sockets()
        for x in range(cpu_sockets):
            cpu_power = float(df['Processor Power_' + str(x) + '(Watt)'].iloc[i])
            power = round(process_utilization/cpu_utilization * cpu_power, 4)
            if x + 1 > len(cpu_power_sum):
                cpu_power_sum.append(0)
            cpu_power_sum[x] += power
            power1 += power

        process_power.append(power1)
        i += 1
    
    average_cpu_power = []
    for x in range(cpu_sockets):
        average_cpu_power.append(cpu_power_sum[x]/i)

    process_cpu_power_df = pd.DataFrame(process_power, columns=['Process CPU Power(Watt)'])
    df1 = pd.concat([df,process_cpu_power_df], axis = 1)
    
    return [average_cpu_power, df1]

def estimate_gpu_power_consumption(nvidia_smi_filename):
    """Estimates the average gpu total power consumption. This function uses the 
    file created by nvidia-smi to have the best accuracy."""

    gpu_df = utils.read_nvidia_smi_file(nvidia_smi_filename)
    gpu_power_sum = []
    gpu_units = len(gpu_df.columns)
    for x in range(gpu_units):
        column = 'power.draw_' + str(x) + ' [W]'
        length = len(gpu_df[column])
        i = 0
        while i < length:
            gpu_power = float(gpu_df[column].iloc[i])
            if x + 1 > len(gpu_power_sum):
                gpu_power_sum.append(0)
            gpu_power_sum[x] += gpu_power
            i += 1
    
    average_gpu_power = []
    for x in range(gpu_units):
        average_gpu_power.append(gpu_power_sum[x]/i)
    
    return [gpu_units,average_gpu_power]

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
    [command,powerlog_filename,process_filename,nvidia_smi_filename,total_process_data,interval,cpu_sockets] = utils.get_configuration()

    """ utils.initialize_files(powerlog_filename, process_filename, nvidia_smi_filename)

    thread_cpu = Process(target = process_cpu_usage, args = (process_filename, 0, ))
    thread_cpu.start()

    pid = cmd.get_gpu_report(nvidia_smi_filename, interval)

    cmd.get_powerlog_report(powerlog_filename, command)
    
    thread_cpu.join()

    cmd.kill_process(pid) """
    
    process_df = join_process_data(powerlog_filename, process_filename, nvidia_smi_filename, cpu_sockets)
    
    elapsed_time = process_df['Elapsed Time (sec)'].iloc[-1]
    average_cpu_power = 0
    if(utils.get_cpu_on()):
        [average_cpu_power,process_df] = estimate_cpu_power_consumption(process_df)
        cpu_sockets = utils.get_physical_cpu_sockets()  
        print("\n-------------------------CPU-------------------------")
        print("Number of CPU Sockets: {}".format(cpu_sockets))
        total_average_cpu_power = 0
        for x in range(cpu_sockets):
            print("\nAverage CPU {} Power: {} Watts".format(x,round(average_cpu_power[x],4)))
            print("CPU {} Energy Consumption: {} Wh".format(x,round(average_cpu_power[x]*elapsed_time/3600,4)))
            total_average_cpu_power += average_cpu_power[x]
        if(cpu_sockets > 1):
            print("\nTotal Average CPU {} Power: {} Watts".format(x,round(total_average_cpu_power,4)))
            print("Total CPU {} Energy Consumption: {} Wh".format(x,round(total_average_cpu_power*elapsed_time/3600,4)))
    
    if(utils.get_gpu_on()):
        [gpu_units,average_gpu_power] = estimate_gpu_power_consumption(nvidia_smi_filename)
        print("\n-------------------------GPU-------------------------")
        print("Number of GPU Units: {}".format(gpu_units))
        total_average_gpu_power = 0    
        for x in range(gpu_units):
            print("\nAverage GPU {} Power: {} Watts".format(x,round(average_gpu_power[x],4)))
            print("GPU {} Energy Consumption: {} Wh".format(x,round(average_gpu_power[x]*elapsed_time/3600,4)))
            total_average_gpu_power += average_gpu_power[x]
        if(gpu_units > 1):
            print("\nTotal Average GPU {} Power: {} Watts".format(x,round(total_average_gpu_power,4)))
            print("Total GPU {} Energy Consumption: {} Wh".format(x,round(total_average_gpu_power*elapsed_time/3600,4)))
    
    average_dram_power = 0
    dram_energy = 0
    if(utils.get_dram_on()):
        [average_dram_power,dram_energy] = estimate_dram_power_consumption(process_df)
        print("\n-------------------------DRAM------------------------")
        print("Average DRAM Power: {} Watts".format(round(average_dram_power,4)))
        print("DRAM Energy Consumption: {} Wh".format(round(dram_energy/3600,4)))
        
    print("\n-------------------------TOTAL-----------------------")
    print("The process lasted: {} Seconds".format(elapsed_time))
    total_consumption = total_average_cpu_power + total_average_gpu_power + average_dram_power
    print("The process consumed: {} Watts".format(round(total_consumption,4)))
    total_consumption = (total_average_cpu_power + total_average_gpu_power) * elapsed_time + dram_energy
    print("The process consumed: {} Wh\n\n".format(round(total_consumption/3600,4)))
    
    process_df.to_csv(total_process_data)

if __name__ == '__main__':
    main()