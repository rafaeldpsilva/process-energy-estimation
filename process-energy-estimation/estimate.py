import configuration
import pandas as pd
import utils

def estimate_cpu_power_consumption(df):
    """Estimates the average cpu power consumption of the process by multiplying 
    the cpu usage of the process by the total cpu power consumption. It uses the 
    dataframe returned by join_process_cpu_usage function so the rows from the cpu pr
    ocess usage matches the right cpu total power consumption rows. This functio
    n also returns a new dataframe with the same information present in the give
    n dataframe and an added column with the cpu process power consumption at a 
    given moment."""
    cpu_power_sum = []
    process_power = []

    i = 0
    length = len(df['Time'])
    while i < length:
        if(configuration.get_cpu_usage_collector()):
            cpu_utilization = float(df['Total CPU Usage(%)'].iloc[i])
        else:
            cpu_utilization = float(df[' CPU Utilization(%)'].iloc[i])
        
        process_utilization = float(df['Process CPU Usage(%)'].iloc[i])
        
        power1 = 0
        cpu_sockets = configuration.get_physical_cpu_sockets()
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

def estimate_gpu_power_consumption(elapsed_time,nvidia_smi_filename):
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
    gpu_energy = []
    for x in range(gpu_units):
        power = gpu_power_sum[x]/i
        average_gpu_power.append(power)
        gpu_energy.append(power*elapsed_time/3600)
    
    return [gpu_units,gpu_energy,average_gpu_power]

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
