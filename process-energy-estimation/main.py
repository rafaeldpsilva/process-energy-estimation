from multiprocessing import Process, Semaphore
from multiprocessing.connection import Listener
import utils
import configuration
import cmd
import convert
import report
import estimate
import psutil
import pandas as pd


def measure_baseline_wattage():
    if(True):
        configuration.initialize_files(configuration.get_powerlog_filename(), configuration.get_process_filename(), configuration.get_nvidia_smi_filename())
        check_seconds = configuration.get_base_check_seconds()
        cmd.get_cpu_base_report(configuration.get_powerlog_filename(), check_seconds)
        cmd.get_gpu_base_report(configuration.get_nvidia_smi_filename(),configuration.get_interval(),check_seconds)
        
    [powerlog_data,general_data] = utils.read_powerlog_file(configuration.get_powerlog_filename(),configuration.get_physical_cpu_sockets())
    array = []
    for i in general_data:
        array.append(i.replace(" ", "").split("="))

    [gpu_units,gpu_energy,average_gpu_power] = estimate.estimate_gpu_power_consumption(float(array[0][1]),configuration.get_nvidia_smi_filename())
    print("Baseline Wattage\n\n========CPU=======\nProcessor Energy: {} Joules\nProcessor Energy: {} mWh\nAverage Processor Power: {} Watt".format(array[2][1],array[3][1],array[4][1]))
    print("========DRAM======\nDRAM Energy: {} Joules\nDRAM Energy: {} mWh\nAverage DRAM Power: {} Watt".format(array[8][1],array[9][1],array[10][1]))
    print("========GPU======\nGPU Energy: {} Joules\nGPU Energy: {} mWh\nAverage GPU Power: {} Watt\n\n".format(gpu_energy[0]*3600,gpu_energy[0],average_gpu_power[0]))

def measure_process_cpu_usage(process_filename, pid):
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
    while process.is_running():
        try:
            process_cpu_usage = process.cpu_percent(interval=0.1)/cpu_count
            total_cpu_usage = psutil.cpu_percent(interval=None)
            #if(process_cpu_usage != 0.0):
            f = open(process_filename, "a")
            f.write(datetime.datetime.now().strftime("%H:%M:%S:%f") + "," + str(process_cpu_usage) + "," + str(total_cpu_usage) + "\n")
            f.close()
        except:
            print("ERROR! CAN'T READ PROCESS CPU USAGE")

def join_process_cpu_usage(powerlog_filename, process_filename, cpu_sockets):
    """Merges the three csv files on a pandas dataframe."""

    [powerlog_data,general_data] = utils.read_powerlog_file(powerlog_filename, cpu_sockets)
    process_data = utils.read_csv_file(process_filename)
    cpu_time_in_microseconds = convert.array_to_microseconds(process_data['Time'],convert.time_to_microsecs)
    cpu_df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)', 'Total CPU Usage(%)'])

    power_draw = []
    length = len(powerlog_data['System Time'])
    i = 0
    while i < length:
        time = convert.time_to_microsecs(powerlog_data['System Time'].iloc[i])
        [cpu_idx,value] = utils.find_nearest(cpu_time_in_microseconds,time)
        cpu_df = pd.concat([cpu_df,process_data.iloc[[cpu_idx],[0,1,2]]], ignore_index = True, axis = 0)      
        i += 1
    
    df = pd.DataFrame(powerlog_data, columns=['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)','Processor Power_1(Watt)','DRAM Power_0(Watt)','Cumulative DRAM Energy_0(Joules)'])

    return pd.concat([df, cpu_df], axis = 1)

def main():
    [command,powerlog_filename,process_filename,nvidia_smi_filename,total_process_data,interval,cpu_sockets] = configuration.get_configuration()

    measure_baseline_wattage()

    if(True):
        configuration.initialize_files(powerlog_filename, process_filename, nvidia_smi_filename)

        thread_cpu = Process(target = measure_process_cpu_usage, args = (process_filename, 0, ))
        thread_cpu.start()

        pid = cmd.get_gpu_report(nvidia_smi_filename, interval)

        cmd.get_powerlog_report(powerlog_filename, command)
        
        thread_cpu.join()

        cmd.kill_process(pid)
    
    process_df = join_process_cpu_usage(powerlog_filename, process_filename, cpu_sockets)
    
    report.print_results(process_df,nvidia_smi_filename,cpu_sockets)
    
    process_df.to_csv(total_process_data)

if __name__ == '__main__':
    main()