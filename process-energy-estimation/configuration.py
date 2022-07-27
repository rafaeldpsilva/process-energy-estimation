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

def initialize_files(powerlog_filename, process_filename, nvidia_smi_filename):
    """Checks if the files with the given names exist, if this is true deletes them."""

    if os.path.exists(powerlog_filename):
        os.remove(powerlog_filename)
    if os.path.exists(process_filename):
        os.remove(process_filename)
    if os.path.exists(nvidia_smi_filename):
        os.remove(nvidia_smi_filename)

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