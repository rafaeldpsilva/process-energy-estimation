import sys
import pandas as pd
from powerlog import *

def read_csv(name):
    data = pd.read_csv (name)  
    df = pd.DataFrame(data)
    df1 = df[:-14]
    return df1
    

def print_base_data(base, base_time):
    print(f'\n\nBase Energy Usage: {base:.3f} Joules')
    print(f'Base Time Elapsed: {base_time:.3f} sec\n\n')

def print_process_data(process_energy_usage, process_time):
    print(f'\n\nProcess Energy Usage: {process_energy_usage:.3f} Joules')
    print(f'Process Time Elapsed: {process_time:.3f} sec\n\n')

def get_base_energy(duration):
    get_base_report(duration)
    
    data = read_csv('./reports/base.csv')
    
    base = data["Cumulative Processor Energy_0(Joules)"].iloc[-1]
    base_time = data["Elapsed Time (sec)"].iloc[-1]
    
    print_base_data(base,base_time)
    return [base, base_time]

def get_process_energy(base, base_time, command):
    get_process_report(command)

    data = read_csv('./reports/process.csv')  

    total = data["Cumulative Processor Energy_0(Joules)"].iloc[-1]
    process_time = data["Elapsed Time (sec)"].iloc[-1]

    base_energy_usage = (base * process_time)/base_time
    process_energy_usage = total - base_energy_usage

    print_process_data(process_energy_usage,process_time)

def evaluate(command):
    [base, base_time] = get_base_energy(5)
    get_process_energy(base, base_time, command)

def main():
    evaluate('"python sorting_algorithms.py"')

if __name__ == '__main__':
   main()