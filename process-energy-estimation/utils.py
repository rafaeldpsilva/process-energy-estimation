import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def initialize_files(powerlog_filename, process_filename, nvidia_smi_filename):
    """Checks if the files with the given names exist, if this is true deletes them."""

    if os.path.exists(powerlog_filename):
        os.remove(powerlog_filename)
    if os.path.exists(process_filename):
        os.remove(process_filename)
    if os.path.exists(nvidia_smi_filename):
        os.remove(nvidia_smi_filename)
  
def find_nearest(array, value):
    """Finds the nearest number specified value in the given array. Returns the index
    of that value and the value itself."""

    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return [idx,array[idx]]

def read_nvidia_smi_file(nvidia_smi_filename):
    """Transforms the file outputed by the nvidia-smi command in a pandas dataframe. 
    Also deletes the "W" present in the power.draw column."""

    gpu_data = pd.read_csv(nvidia_smi_filename)
    df = pd.DataFrame(gpu_data)
    df.columns = ['index','timestamp','power.draw [W]']
    
    power_draw = []
    index = []
    length = len(df['timestamp'])
    i = 0
    while i < length:
        p = df['power.draw [W]'].iloc[i][:-2]
        power_draw.append(float(p.strip()))
        index.append(i)
        i += 1
    
    power_draw_df = pd.DataFrame(power_draw, columns =['power.draw [W]'])
    index_df = pd.DataFrame(index, columns =['index'])
    return pd.concat([index_df, power_draw_df], axis = 1)
    
def read_powerlog_file(powerlog_filename):
    """Transforms the file outputed by the powerlog3.0 tool in a pandas dataframe. 
    Also deletes the last 14 rows present in the first column of the file"""

    data = pd.read_csv(powerlog_filename)  
    df = pd.DataFrame(data)
    df1 = df[:-14]
    return df1

def read_csv_file(powerlog_filename):
    """Reads a specified csv file and transforms it in a pandas dataframe."""
    
    data = pd.read_csv(powerlog_filename)  
    return pd.DataFrame(data)

def read_txt(name):
    """Reads a specified txt file and transforms it in a pandas dataframe."""

    with open(name) as f:
        lines = f.readlines()
    
    df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)'])
    
    for line in lines:
        split = line.split()
        data = pd.DataFrame([[split[0], split[1]]], columns=['Time','Process CPU Usage(%)'])
        df = pd.concat([df,data], ignore_index = True, axis = 0)

    return df

def plot_power(df):
    """Plots the cpu total power consumption and the cpu process power consumption, t
    hrought time."""

    plt.plot(df['Elapsed Time (sec)'], df['Processor Power_0(Watt)'], label='Energia Consumida pelo Sistema no CPU')
    plt.plot(df['Elapsed Time (sec)'],df['Process CPU Power(Watt)'], label='Energia Consumida pelo Processo no CPU')
    #plt.plot(df['Elapsed Time (sec)'],df['power.draw [W]'], label='Energia Consumida pela GPU')
    plt.legend()
    plt.show()

def plot_gpu_power(nvidia_smi_filename):
    """Plots the gpu total power consumption throught time."""

    gpu_df = read_nvidia_smi_file(nvidia_smi_filename)
    
    plt.plot(gpu_df['index'], gpu_df['power.draw [W]'], label='Energia Consumida pela GPU', color = 'green')
    plt.legend()
    plt.show()

def plot_usage(df):
    """Plots the total cpu usage and the process cpu usage, throught time."""

    plt.plot(df['Elapsed Time (sec)'], df['Process CPU Usage(%)'], label='Process CPU Usage(%)')
    plt.plot(df['Elapsed Time (sec)'], df[' CPU Utilization(%)'], label='CPU Utilization(%)')
    plt.ylim([0,110])
    plt.legend()
    plt.show()

def print_results(elapsed_time,cpu_consumption,gpu_consumption,dram_consumption,dram_energy):
    """Prints the results of the process energy and power consumption estimation."""
    
    total_consumption = cpu_consumption + gpu_consumption+dram_consumption
    print("\nThe process lasted: " + str(elapsed_time) + " Seconds")
    print("The process consumed: " + str(round(total_consumption,4)) + " Watts")
    print("CPU: " + str(round(cpu_consumption,4)) + " Watts" + " | GPU: " + str(round(gpu_consumption,4)) + " Watts" + " | DRAM: " + str(round(dram_consumption,4)) + " Watts")
    total_consumption = (cpu_consumption + gpu_consumption) * elapsed_time + dram_energy
    print("The process consumed: " + str(round(total_consumption/3600,4)) + " Wh")

def time_to_microsecs(string):
    """Formats a string with this time format - 00:00:00:000 - in microseconds."""

    hours = int(string[0:2]) * 3600000000
    minutes = int(string[3:5]) * 60000000 
    seconds = int(string[6:8]) * 1000000
    microseconds = int(string [9:12]) + hours + minutes + seconds
    return microseconds

def datatime_to_microsecs(string):
    """Formats a string with this time format - 0000/00/00 00:00:00.000 - in microseconds."""

    hours = int(string[12:14]) * 3600000000
    minutes = int(string[15:17]) * 60000000 
    seconds = int(string[18:20]) * 1000000
    microseconds = int(string [21:24]) + hours + minutes + seconds
    return microseconds

def array_to_microseconds(array,function):
    """Tranforms a given array of strings with a certain time format into microseconds by 
    making each element of the array go throught a given function."""
    
    array1 = []
    for line in array:
        time = function(line)
        array1.append(time)
    return array1