import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
  
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
        gpu = df['index'].iloc[i]
        if gpu + 1 > len(power_draw):
            power_draw.append([])
        power = df['power.draw [W]'].iloc[i][:-2]
        power_draw[gpu].append(float(power.strip()))
        index.append(i)
        i += 1
    
    gpu_df = pd.DataFrame()
    
    for x in range(len(power_draw)):
        power_draw_df = pd.DataFrame(power_draw[x], columns =['power.draw_' + str(x) + ' [W]'])
        gpu_df = pd.concat([gpu_df, power_draw_df], axis = 1)
    return gpu_df
    
def read_powerlog_file(powerlog_filename, cpu_sockets):
    """Transforms the file outputed by the powerlog3.0 tool in a pandas dataframe. 
    Also deletes the last 14 rows present in the first column of the file"""

    data = pd.read_csv(powerlog_filename)  
    df = pd.DataFrame(data)
    n_tail = 5 + (cpu_sockets * 9)
    df1 = df[:-n_tail]
    return df1

def read_csv_file(powerlog_filename):
    """Reads a specified csv file and transforms it in a pandas dataframe."""
    
    data = pd.read_csv(powerlog_filename)  
    return pd.DataFrame(data)

def read_txt(name):
    """Reads a specified txt file and transforms it in a pandas dataframe."""

    with open(name) as f:
        lines = f.readlines()
    
    df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)', 'Total CPU Usage(%)'])
    
    for line in lines:
        split = line.split()
        data = pd.DataFrame([[split[0], split[1]]], columns=['Time','Process CPU Usage(%)', 'Total CPU Usage(%)'])
        df = pd.concat([df,data], ignore_index = True, axis = 0)

    return df