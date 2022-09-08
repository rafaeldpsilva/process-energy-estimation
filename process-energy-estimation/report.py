import estimate
import configuration
import matplotlib.pyplot as plt

def plot_power(df):
    """Plots the cpu total power consumption and the cpu process power consumption, t
    hrought time."""

    plt.plot(df['Elapsed Time (sec)'], df['DRAM Power_0(Watt)'], label='DRAM')
    plt.plot(df['Elapsed Time (sec)'], df['Process CPU Power(Watt)'], label='CPU')
    plt.plot(df['Elapsed Time (sec)'], df['Total GPU Power(Watt)'], label='GPU')
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

def print_base_results(elapsed_time,cpu,dram):
    print("\n\nBaseline Consumption")
    total_average_cpu_power = 0
    total_cpu_energy = 0
    if(configuration.get_cpu_on()):
        cpu_sockets = configuration.get_physical_cpu_sockets()  
        print("\n-------------------------CPU-------------------------")
        print("Number of CPU Sockets: {}".format(cpu_sockets))
        for x in range(cpu_sockets):
            print("\nAverage CPU {} Power: {} Watts".format(x,round(cpu[x][1],4)))
            print("CPU {} Energy Consumption: {} Wh".format(x,round(cpu[x][0],4)))
            total_average_cpu_power += cpu[x][1]
            total_cpu_energy += cpu[x][0]
        if(cpu_sockets > 1):
            print("\nTotal Average CPU {} Power: {} Watts".format(x,round(total_average_cpu_power,4)))
            print("Total CPU {} Energy Consumption: {} Wh".format(x,round(total_cpu_energy,4)))

    total_average_gpu_power = 0
    total_gpu_energy = 0   
    if(configuration.get_gpu_on()):
        [gpu_units,gpu_energy,average_gpu_power,gpu_df] = estimate.estimate_gpu_power_consumption(elapsed_time,configuration.get_base_nvidia_smi_filename())
        print("\n-------------------------GPU-------------------------")
        print("Number of GPU Units: {}".format(gpu_units))
        for x in range(gpu_units):
            print("\nAverage GPU {} Power: {} Watts".format(x,round(average_gpu_power[x],4)))
            print("GPU {} Energy Consumption: {} Wh".format(x,round(gpu_energy[x],4)))
            total_average_gpu_power += average_gpu_power[x]
            total_gpu_energy += gpu_energy[x]
        if(gpu_units > 1):
            print("\nTotal Average GPU {} Power: {} Watts".format(x,round(total_average_gpu_power,4)))
            print("Total GPU {} Energy Consumption: {} Wh".format(x,round(total_gpu_energy,4)))

    average_dram_power = 0
    dram_energy = 0
    if(configuration.get_dram_on()):
        average_dram_power = dram[1]
        dram_energy = dram[0]
        print("\n-------------------------DRAM------------------------")
        print("Average DRAM Power: {} Watts".format(round(average_dram_power,4)))
        print("DRAM Energy Consumption: {} Wh".format(round(dram_energy,4)))
        
    print("\n-------------------------TOTAL-----------------------")
    print("The measurement lasted: {} Seconds".format(elapsed_time))
    total_consumption = total_average_cpu_power + total_average_gpu_power + average_dram_power
    print("Baseline consumption: {} Watts".format(round(total_consumption,4)))
    total_consumption = (total_average_cpu_power + total_average_gpu_power) * elapsed_time + dram_energy
    print("Baseline consumption: {} Wh\n\n".format(round(total_consumption/3600,4)))

    base_reports_path = configuration.get_base_reports_path()
    gpu_df.to_csv(base_reports_path+"/show_base_gpu.csv")

def print_results(process_df,nvidia_smi_filename,cpu_sockets):
    print("\n\nProcess Consumption")
    elapsed_time = process_df['Elapsed Time (sec)'].iloc[-1]
    
    total_average_cpu_power = 0
    if(configuration.get_cpu_on()):
        [average_cpu_power,process_df] = estimate.estimate_cpu_power_consumption(process_df)
        cpu_sockets = configuration.get_physical_cpu_sockets()  
        print("\n-------------------------CPU-------------------------")
        print("Number of CPU Sockets: {}".format(cpu_sockets))
        for x in range(cpu_sockets):
            print("\nAverage CPU {} Power: {} Watts".format(x,round(average_cpu_power[x],4)))
            print("CPU {} Energy Consumption: {} Wh".format(x,round(average_cpu_power[x]*elapsed_time/3600,4)))
            total_average_cpu_power += average_cpu_power[x]
        if(cpu_sockets > 1):
            print("\nTotal Average CPU {} Power: {} Watts".format(x,round(total_average_cpu_power,4)))
            print("Total CPU {} Energy Consumption: {} Wh".format(x,round(total_average_cpu_power*elapsed_time/3600,4)))
    
    total_average_gpu_power = 0
    total_gpu_energy = 0   
    if(configuration.get_gpu_on()):
        [gpu_units,gpu_energy,average_gpu_power, gpu_df] = estimate.estimate_gpu_power_consumption(elapsed_time,configuration.get_nvidia_smi_filename())
        print("\n-------------------------GPU-------------------------")
        print("Number of GPU Units: {}".format(gpu_units))
        for x in range(gpu_units):
            print("\nAverage GPU {} Power: {} Watts".format(x,round(average_gpu_power[x],4)))
            print("GPU {} Energy Consumption: {} Wh".format(x,round(gpu_energy[x],4)))
            total_average_gpu_power += average_gpu_power[x]
            total_gpu_energy += gpu_energy[x]
        if(gpu_units > 1):
            print("\nTotal Average GPU {} Power: {} Watts".format(x,round(total_average_gpu_power,4)))
            print("Total GPU {} Energy Consumption: {} Wh".format(x,round(total_gpu_energy,4)))
    
    average_dram_power = 0
    dram_energy = 0
    if(configuration.get_dram_on()):
        [average_dram_power,dram_energy] = estimate.estimate_dram_power_consumption(process_df)
        print("\n-------------------------DRAM------------------------")
        print("Average DRAM Power: {} Watts".format(round(average_dram_power,4)))
        print("DRAM Energy Consumption: {} Wh".format(round(dram_energy/3600,4)))
        
    print("\n-------------------------TOTAL-----------------------")
    print("The process lasted: {} Seconds".format(elapsed_time))
    total_consumption = total_average_cpu_power + total_average_gpu_power + average_dram_power
    print("The process consumed: {} Watts".format(round(total_consumption,4)))
    total_consumption = (total_average_cpu_power + total_average_gpu_power) * elapsed_time + dram_energy
    print("The process consumed: {} Wh\n\n".format(round(total_consumption/3600,4)))

    total_process_data_filename = configuration.get_total_process_data_filename()
    process_df.to_csv(total_process_data_filename)
    reports_path = configuration.get_reports_path()
    gpu_df.to_csv(reports_path+"/show_gpu.csv")
