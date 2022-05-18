import pandas as pd
import numpy as np

#Utils
SYSTEM_TIME = 0
RDTSC = 1
ELAPSED_TIME = 2
CPU_UTILIZATION = 3
CPU_FREQUENCY = 4
PROCESSOR_POWER = 5
CUMULATIVE_PROCESSOR_ENERGY = 6
CUMULATIVE_PROCESSOR_ENERGY = 7
IA_POWER = 8
CUMULATIVE_IA_ENERGY = 9
CUMULATIVE_IA_ENERGY = 10
PACKAGE_TEMPERATURE = 11
PACKAGE_HOT = 12
DRAM_POWER = 13
CUMULATIVE_DRAM_ENERGY = 14
CUMULATIVE_DRAM_ENERGY = 15
GT_POWER = 16
CUMULATIVE_GT_ENERGY = 17
CUMULATIVE_GT_ENERGY = 18
PACKAGE_PL1 = 19
PACKAGE_PL2 = 20
PACKAGE_PL4 = 21
PLATFORM_PSYSPL1 = 22
PLATFORM_PSYSPL2 = 23
GT_FREQUENCY = 24
GT_UTILIZATION = 25 

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return [idx,array[idx]]

def read_csv(name):
    data = pd.read_csv (name)  
    df = pd.DataFrame(data)
    df1 = df[:-14]
    return df1

def read_txt(name):
    with open(name) as f:
        lines = f.readlines()
    
    df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)'])
    
    for line in lines:
        split = line.split()
        data = pd.DataFrame([[split[0], split[1]]], columns=['Time','Process CPU Usage(%)'])
        df = pd.concat([df,data], ignore_index = True, axis = 0)

    return df

# format : 00:00:00:000
def to_microsecs(string):
    hours = int(string[0:2]) * 3600000000
    minutes = int(string[3:5]) * 60000000 
    seconds = int(string[6:8]) * 1000000
    microseconds = int(string [9:12] +  "00") + hours + minutes + seconds
    return microseconds