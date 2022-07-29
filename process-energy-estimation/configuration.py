import json
import os

def get_configuration():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
        
    command = configuration['COMMAND']
    powerlog_filename = configuration['POWERLOG_FILENAME']
    process_filename = configuration['PROCESS_FILENAME']
    nvidia_smi_filename = configuration['NVIDIA_SMI_FILENAME']
    total_process_data = configuration['TOTAL_PROCESS_DATA']
    interval = configuration['INTERVAL']
    cpu_sockets = configuration['PHYSICAL_CPU_SOCKETS']

    return [command,powerlog_filename,process_filename,nvidia_smi_filename,total_process_data,interval,cpu_sockets]

def initialize_files():
    """Checks if the files with the given names exist, if this is true deletes them."""
    reports_path = get_reports_path()
    base_reports_path = get_base_reports_path()
    powerlog_filename = get_powerlog_filename()
    process_filename = get_process_filename()
    nvidia_smi_filename = get_nvidia_smi_filename()

    if not os.path.exists(reports_path):
        os.mkdir(reports_path)
    if not os.path.exists(base_reports_path):
        os.mkdir(base_reports_path)
    if os.path.exists(powerlog_filename):
        os.remove(powerlog_filename)
    if os.path.exists(process_filename):
        os.remove(process_filename)
    if os.path.exists(nvidia_smi_filename):
        os.remove(nvidia_smi_filename)

def get_base_check_seconds():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['BASE_CHECK_SECONDS']

def get_reports_path():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['REPORTS_PATH']

def get_base_reports_path():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    
    reports_path = configuration['REPORTS_PATH']
    return os.path.join(reports_path, "base/")

def get_base_filename():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    
    reports_path = configuration['REPORTS_PATH']
    base_filename = configuration['BASE_FILENAME']
    return os.path.join(reports_path, "base/", base_filename)

def get_powerlog_filename():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    reports_path = configuration['REPORTS_PATH']
    powerlog_filename = configuration['POWERLOG_FILENAME']
    return os.path.join(reports_path, powerlog_filename)

def get_process_filename():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    
    reports_path = configuration['REPORTS_PATH']
    process_filename = configuration['PROCESS_FILENAME']
    return os.path.join(reports_path, process_filename)

def get_nvidia_smi_filename():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    
    reports_path = configuration['REPORTS_PATH']
    nvidia_smi_filename = configuration['NVIDIA_SMI_FILENAME']
    return os.path.join(reports_path, nvidia_smi_filename)

def get_total_process_data_filename():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    reports_path = configuration['REPORTS_PATH']
    total_process_data_filename = configuration['TOTAL_PROCESS_DATA']
    return os.path.join(reports_path, total_process_data_filename)

def get_interval():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['INTERVAL']

def get_physical_cpu_sockets():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['PHYSICAL_CPU_SOCKETS']

def get_cpu_on():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['CPU']

def get_gpu_on():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['GPU']

def get_dram_on():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['DRAM']

def get_cpu_usage_collector():
    with open("./process-energy-estimation/configuration.json") as json_file:
            configuration = json.load(json_file)
    return configuration['CPU_USAGE_COLLECTOR']