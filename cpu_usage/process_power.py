import subprocess

def main():
    subprocess.call('\& "C:\Program Files\Intel\Power Gadget 3.6\PowerLog3.0.exe" -cmd "python process.py" ', shell=True)

if __name__ == '__main__':
   main()