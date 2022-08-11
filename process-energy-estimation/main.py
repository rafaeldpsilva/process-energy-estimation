from multiprocessing import Process, Pipe
from multiprocessing.connection import Listener
import utils
import configuration
import cmd
import convert
import report
import estimate
import psutil
import datetime
import pandas as pd

def run_auxiliary_command():
    parent_conn, child_conn = Pipe()
    command = Process(target = cmd.run_command, args = (configuration.get_auxiliary_command(), child_conn, ))
    command.start()
    pid = parent_conn.recv()
    return pid

def measure_baseline_wattage():
    check_seconds = configuration.get_base_check_seconds()
    cmd.get_cpu_base_report(configuration.get_base_powerlog_filename(), check_seconds)
    cmd.get_gpu_base_report(configuration.get_base_nvidia_smi_filename(),configuration.get_interval(),check_seconds)
    
    physical_cpu_sockets = configuration.get_physical_cpu_sockets()
    [powerlog_data,general_data] = utils.read_powerlog_file(configuration.get_base_powerlog_filename(),physical_cpu_sockets)
    general_data_array = []
    for i in general_data:
        general_data_array.append(i.replace(" ", "").split("="))
    
    elapsed_time = float(general_data_array[0][1])

    cpu = []
    for i in range(physical_cpu_sockets):
        energy = float(general_data_array[2+(i*9)][1])/3600
        power = float(general_data_array[2+2+(i*9)][1])
        cpu.append([energy,power])
    
    dram = []
    energy = float(general_data_array[(physical_cpu_sockets*9)-1][1])/3600
    dram.append(energy)
    power = float(general_data_array[1+(physical_cpu_sockets*9)][1])
    dram.append(power)

    report.print_base_results(elapsed_time,cpu,dram)

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
    file = ""
    while True:
        try:
            time = datetime.datetime.now().strftime("%H:%M:%S:%f")
            process_cpu_usage = process.cpu_percent(interval=0.1)/cpu_count
            total_cpu_usage = psutil.cpu_percent(interval=None)
            if(process_cpu_usage != 0.0):
                file += time + "," + str(process_cpu_usage) + "," + str(total_cpu_usage) + "\n"
        except:
            f = open(process_filename, "a")
            f.write(file)
            f.close()
            return 0

def join_process_cpu_usage(powerlog_filename, process_filename, cpu_sockets):
    """Merges the three csv files on a pandas dataframe."""

    [powerlog_data,general_data] = utils.read_powerlog_file(powerlog_filename, cpu_sockets)
    process_data = utils.read_csv_file(process_filename)
    cpu_time_in_microseconds = convert.array_to_microseconds(process_data['Time'],convert.time_to_microsecs)

    nvidia_df = utils.read_nvidia_smi_file(configuration.get_nvidia_smi_filename())
    gpu_time_in_microseconds = []
    gpu_units = int(len(nvidia_df.columns)/2)
    for x in range(gpu_units):
        gpu_time_in_microseconds.append(convert.array_to_microseconds(nvidia_df['timestamp_'+str(x)],convert.datatime_to_microsecs))
    
    cpu_df = pd.DataFrame([], columns =['Time', 'Process CPU Usage(%)', 'Total CPU Usage(%)'])

    gpu_array = []
    length = len(powerlog_data['System Time'])
    last_idx = -1
    i = 0
    while i < length:
        #CPU USAGE
        time = convert.time_to_microsecs(powerlog_data['System Time'].iloc[i])
        [cpu_idx,value] = utils.find_nearest(cpu_time_in_microseconds,time)        
        cpu_df = pd.concat([cpu_df,process_data.iloc[[cpu_idx],[0,1,2]]], ignore_index = True, axis = 0)

        #GPU
        temp_array = []
        total_sum = 0
        for x in range(gpu_units):
            temp_array,last_idx,total_sum = add_gpu(gpu_time_in_microseconds, x, nvidia_df, time,last_idx,temp_array,total_sum)
        
        print(total_sum)
        temp_array.append(total_sum)
        gpu_array.append(temp_array)
        i += 1
    
    df = pd.DataFrame(powerlog_data, columns=['System Time','Elapsed Time (sec)',' CPU Utilization(%)','Processor Power_0(Watt)','Processor Power_1(Watt)','DRAM Power_0(Watt)','Cumulative DRAM Energy_0(Joules)'])
    df = pd.concat([df, cpu_df], axis = 1)

    col = []
    for x in range(gpu_units):
        col.append('timestamp_'+str(x))
        col.append('GPU Power_'+str(x)+'(Watt)')
    col.append('Total GPU Power'+str(x)+'(Watt)')
    
    gpu_df = pd.DataFrame(gpu_array, columns =col)
    return pd.concat([df, gpu_df], axis = 1)

def add_gpu(gpu_time_in_microseconds, x, nvidia_df,time,last_idx,temp_array,total_sum):
    [gpu_idx,value] = utils.find_nearest(gpu_time_in_microseconds[x],time)
    dif = gpu_idx - last_idx        
    if dif > 1:
        sum = 0
        while last_idx < gpu_idx:
            last_idx += 1        
            sum += float(nvidia_df['power.draw_'+str(x)+' [W]'].iloc[last_idx])
        total = sum/dif
    else:
        total = float(nvidia_df['power.draw_'+str(x)+' [W]'].iloc[last_idx])
    last_idx = gpu_idx

    temp_array.append(str(nvidia_df['timestamp_'+str(x)].iloc[gpu_idx]))
    temp_array.append(total)
    total_sum += total

    return temp_array,last_idx,total_sum

def main():
    aux_pid = run_auxiliary_command()
    
    configuration.initialize_files()
    measure_baseline_wattage()
    
    powerlog_filename = configuration.get_powerlog_filename()
    nvidia_smi_filename = configuration.get_nvidia_smi_filename()
    process_filename = configuration.get_process_filename()
    
    if(True):
        thread_cpu = Process(target = measure_process_cpu_usage, args = (configuration.get_process_filename(), 0, ))
        thread_cpu.start()

        pid = cmd.get_gpu_report(nvidia_smi_filename, configuration.get_interval())

        cmd.get_powerlog_report(powerlog_filename, configuration.get_command())
        
        thread_cpu.join()

        cmd.kill_process(pid)
    
    if psutil.pid_exists(aux_pid):
        cmd.kill_process(aux_pid)

    cpu_sockets = configuration.get_physical_cpu_sockets()

    process_df = join_process_cpu_usage(powerlog_filename, configuration.get_process_filename(), cpu_sockets)
    
    report.print_results(process_df,nvidia_smi_filename,cpu_sockets)

    total_process_data_filename = configuration.get_total_process_data_filename()
    total_process_data = utils.read_csv_file(total_process_data_filename)
    report.plot_power(total_process_data)

if __name__ == '__main__':
    main()