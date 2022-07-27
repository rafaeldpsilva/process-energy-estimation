from multiprocessing import Process, Semaphore
from multiprocessing.connection import Listener
import utils
import configuration
import cmd
import convert
import report
import psutil
import pandas as pd



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
            return 0

def join_process_cpu_usage(powerlog_filename, process_filename, cpu_sockets):
    """Merges the three csv files on a pandas dataframe."""

    powerlog_data = utils.read_powerlog_file(powerlog_filename, cpu_sockets)
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

    if(False):
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