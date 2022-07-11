
# Process Energy Estimation

Estimate and track the energy consumption of your software, quantify and analyze their impact.

<br/>

[![](https://anaconda.org/conda-forge/codecarbon/badges/version.svg)](https://anaconda.org/conda-forge/codecarbon)
[![](https://img.shields.io/pypi/v/codecarbon?color=024758)](https://pypi.org/project/codecarbon/)


- [About Process Energy Estimation 💡](#about-process-energy-estimation-)
- [Installation](#installation)
      - [Using git](#install-using-git)
      - [Intel Power Gadget](#install-intel-power-gadget)
      - [Nvidia System Management Interface](#install-nvidia-system-management-interface)
      - [Install dependencies](#install-dependencies)
- [Quickstart 🚀](#quickstart-)
    - [Configuration](#configuration)
- [Examples 🐤](#examples-)
- [Infrastructure Support 🖥️](#infrastructure-support-️)
    - [GPU](#gpu)
    - [CPU](#cpu)
      - [On Windows and Mac](#on-windows-and-mac)
      - [On Linux](#on-linux)
      - [On all platforms](#on-all-platforms)
- [Contact 📝](#contact-)

# About Process Energy Estimation 💡

While computing currently represents roughly 0.5% of the world’s energy consumption, that percentage is projected to grow beyond 2% in the coming years, which will entail a significant rise in global CO2 emissions if not done properly. Given this increase, it is important to quantify and track the extent and origin of this energy usage, and to minimize the emissions incurred as much as possible.

The concept of green computing promotes the eficient use of  computational processing resources that are normally used without regard to the respective energy cost.

For this purpose, we created **Process Energy Estimation**, a Python package for tracking the energy consumed by computer programs, from straightforward algorithms to deep neural networks.

By taking into account your computing hardware, usage and running time, Process Energy Estimation can provide an estimate of how much energy you consumed.

Follow the steps below to set up the package and don't hesitate to open an issue if you need help!

# Installation
In the root of your project, clone or download the repository present in [this github page](https://github.com/rafaeldpsilva/process-energy-monitor)

### Using git

```
git clone https://github.com/rafaeldpsilva/process-energy-monitor.git
````
## Intel Power Gadget

To install Intel Power Gadget, follow the instructions given on [this website](https://www.intel.com/content/www/us/en/developer/articles/tool/power-gadget.html)

After the successful install, add the path of the folder where the tool is installed to the `$PATH` environment variable.

Check if it is installed correctly by running the following command in the terminal:
```
PowerLog3.0.exe -h
````

## Nvidia System Management Interface

The nvidia-smi utility normally gets installed in the driver install step. It cannot/does not get installed in any other installation step.

If you install a NVIDIA GPU driver using a repository that is maintained by NVIDIA, you will always get the nvidia-smi utility with any recent driver install.

You can check if it is installed correctly by running the following command in your terminal:
```
nvidia-smi -h
````
## Dependencies

In order to run the code successfully you also need to install some dependencies. Run this three commands to do so:

```
pip install pandas
pip install matplotlib
pip install psutil
````


`process-energy-estimation` is now installed in your the local environment

# Quickstart 🚀

### Configuration
This software needs to be configured through a file in a json format, similar to this:

```json
{
    "COMMAND" : "python sorting_algorithms.py", 
    "POWERLOG_FILENAME" : "./process-energy-estimation/reports/powerlog.csv",
    "PROCESS_FILENAME" : "./process-energy-estimation/reports/process.csv",
    "NVIDIA_SMI_FILENAME" : "./process-energy-estimation/reports/nvidia.csv",
    "TOTAL_PROCESS_DATA" : "./process-energy-estimation/reports/total_process_data.csv",
    "INTERVAL" : 100,
    "CPU": 1,
    "GPU": 0,
    "DRAM": 1
}
```

CodeCarbon will look sequentially for arguments in:

- `COMMAND`: the command line to run the software you pretend to measure
- `POWERLOG_FILENAME`: name/path of the file in which the data from Inter Power Gadget will be saved
- `PROCESS_FILENAME`: name/path of the file in which the process cpu usage data will be saved
- `NVIDIA_SMI_FILENAME`: name/path of the file in which the data from Nvidia System Management Interface will be saved
- `TOTAL_PROCESS_DATA`: name/path of the file in which the data created by the two tools and the system will be saved
- `INTERVAL`: miliseconds interval to read the GPU information
- `CPU`: 1 or 0 if the component energy consumption is taken in consideration or not, respectively
- `GPU`: 1 or 0 if the component energy consumption is taken in consideration or not, respectively
- `DRAM`: 1 or 0 if the component energy consumption is taken in consideration or not, respectively

# Examples 🐤
As an illustration of how to use Process Energy Estimation, we created a simple example using the sorting algorithm [Stooge Sort](https://www.geeksforgeeks.org/stooge-sort/):

In the [`examples/`](/examples/) folder run:

```
python ./process-energy-estimation/main.py
```
Which should output something like the following lines:

```ProcessReport
Max Temp = 100
number of nodes = 1
TDP(mWh)_0 = 15.00
Base Frequency = 2001.00(MHz)
Logging...Done

The process lasted: 10.469 Seconds
The process consumed: 4.2477 Watts
CPU: 3.6233 Watts | GPU: 0 Watts | DRAM: 0.6244 Watts
The process consumed: 0.0123 Wh
```
This will also create four `.csv` files in the [`reports/`](/examples/reports/) folder with information created by this system, Intel Power Gadget and Nvidia System Management Interface, in the respective files.

# Infrastructure Support 🖥️
Currently the package supports following hardware infrastructure.

### GPU
- Tracks Nvidia GPUs power consumption using `nvidia-smi` command.

### CPU

#### Windows
- Tracks Intel processors power consumption using the `Intel Power Gadget`
- You need to **[install it independently](https://software.intel.com/content/www/us/en/develop/articles/intel-power-gadget.html)** for Process Energy Consumption to function.

# Contact 📝

Maintainers are [@rafaeldpsilva](https://github.com/rafaeldpsilva). Process Energy Estimation is developed by researchers from [**GECAD**](https://www.gecad.isep.ipp.pt).