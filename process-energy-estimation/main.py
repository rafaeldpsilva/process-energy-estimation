from multiprocessing import Process, Semaphore
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

def energy(user_func, *args, powerLoss = 0.8, year, printToScreen, timeseries):
    """ Evaluates the kwh needed for your code to run
    Parameters:
       user_func (function): user's function
    Returns:
        (process_kwh, return_value, watt_averages)
    """

    baseline_check_seconds = 5
    files, multiple_cpus = utils.get_files()
    is_nvidia_gpu = utils.valid_gpu()
    is_valid_cpu = utils.valid_cpu()

    # GPU handling if Nvidia
    gpu_baseline =[0]
    gpu_process = [0]
    bash_command = "nvidia-smi -i 0 --format=csv,noheader --query-gpu=power.draw"

    time_baseline = []
    reading_baseline_wattage = []

    time_process = []
    reading_process_wattage = []

    for i in range(int(baseline_check_seconds / DELAY)):
        if is_nvidia_gpu:
            output = subprocess.check_output(['bash','-c', bash_command])
            output = float(output.decode("utf-8")[:-2])
            gpu_baseline.append(output)
        if is_valid_cpu:
            files = utils.measure_files(files, DELAY)
            files = utils.update_files(files)
        else:
            time.sleep(DELAY)
        # Adds the most recent value of GPU; 0 if not Nvidia
        last_reading = utils.get_total(files, multiple_cpus) + gpu_baseline[-1]
        if last_reading >=0 and printToScreen:
            utils.log("Baseline wattage", last_reading)
            time = round(i* DELAY, 1)
            time_baseline.append(time)
            reading_baseline_wattage.append(last_reading)
    if timeseries:
        with open('baseline_wattage.csv', 'w') as baseline_wattage_file:
            baseline_wattage_writer = csv.writer(baseline_wattage_file)
            baseline_wattage_writer.writerow(["time", "baseline wattage reading"])
            for i in range(len(time_baseline)):
                baseline_wattage_writer.writerow([time_baseline[i], reading_baseline_wattage[i]])
    if printToScreen:
        utils.newline()

    # Running the process and measuring wattage
    q = Queue()
    p = Process(target = func, args = (user_func, q, *args,))

    start = timer()
    small_delay_counter = 0
    return_value = None
    p.start()

    while(p.is_alive()):
        # Checking at a faster rate for quick processes
        if (small_delay_counter > DELAY):
            delay = DELAY / 10
            small_delay_counter+=1
        else:
            delay = DELAY

        if is_nvidia_gpu:
            output = subprocess.check_output(['bash','-c', bash_command])
            output = float(output.decode("utf-8")[:-2])
            gpu_process.append(output)
        if is_valid_cpu:
            files = utils.measure_files(files, delay)
            files = utils.update_files(files, True)
        else:
            time.sleep(delay)
        # Just output, not added
        last_reading = (utils.get_total(files, multiple_cpus) + gpu_process[-1]) / powerLoss
        if last_reading >=0 and printToScreen:
            utils.log("Process wattage", last_reading)
            time = round(timer()-start, 1)
            time_process.append(time)
            reading_process_wattage.append(last_reading)
        # Getting the return value of the user's function
        try:
            return_value = q.get_nowait()
            break
        except queue.Empty:
            pass
    if timeseries:
        with open('process_wattage.csv', 'w') as process_wattage_file:
            process_wattage_writer = csv.writer(process_wattage_file)
            process_wattage_writer.writerow(["time", "process wattage reading"])
            for i in range(len(time_process)):
                process_wattage_writer.writerow([time_process[i], reading_process_wattage[i]])
    p.join()
    end = timer()
    for file in files:
        file.process = file.process[1:-1]
        file.baseline = file.baseline[1:-1]
    if is_nvidia_gpu:
        gpu_baseline_average = statistics.mean(gpu_baseline[2:-1])
        gpu_process_average = statistics.mean(gpu_process[2:-1])
    else:
        gpu_baseline_average = 0
        gpu_process_average = 0

    total_time = end-start # seconds
    # Formatting the time nicely
    timedelta = str(datetime.timedelta(seconds=total_time)).split('.')[0]

    if files[0].process == []:
        raise Exception("Process executed too fast to gather energy consumption")
    files = utils.average_files(files)

    process_average = utils.get_process_average(files, multiple_cpus, gpu_process_average)
    baseline_average = utils.get_baseline_average(files, multiple_cpus, gpu_baseline_average)
    difference_average = process_average - baseline_average
    watt_averages = [baseline_average, process_average, difference_average, timedelta]

    # Subtracting baseline wattage to get more accurate result
    process_kwh = convert.to_kwh((process_average - baseline_average)*total_time) / powerLoss

    if is_nvidia_gpu:
        gpu_file = file("GPU", "")
        gpu_file.create_gpu(gpu_baseline_average, gpu_process_average)
        files.append(file("GPU", ""))

    # Logging
    if printToScreen:
        utils.log("Final Readings", baseline_average, process_average, difference_average, timedelta)
    return (process_kwh, return_value, watt_averages, files, total_time, time_baseline, reading_baseline_wattage, time_process, reading_process_wattage)

def measure_baseline_wattage():
    if(True):
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
    while True:
        try:
            time = datetime.datetime.now().strftime("%H:%M:%S:%f")
            process_cpu_usage = process.cpu_percent(interval=0.1)/cpu_count
            total_cpu_usage = psutil.cpu_percent(interval=None)
            if(process_cpu_usage != 0.0):
                f = open(process_filename, "a")
                f.write(time + "," + str(process_cpu_usage) + "," + str(total_cpu_usage) + "\n")
                f.close()
        except:
            return 0

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
    
    cpu_sockets = configuration.get_physical_cpu_sockets()

    process_df = join_process_cpu_usage(powerlog_filename, configuration.get_process_filename(), cpu_sockets)
    
    report.print_results(process_df,nvidia_smi_filename,cpu_sockets)
    
    total_process_data_filename = configuration.get_total_process_data_filename()
    process_df.to_csv(total_process_data_filename)

if __name__ == '__main__':
    main()