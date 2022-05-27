pip install psutil
pip install pandas
pip install datetime
pip install matplotlib
pip install numpy
pip install subprocess
pip install os-sys
cd C:\Windows\System32\DriverStore\FileRepository\nv_dispswi.inf_amd64_857d0ac7bf001fe7
nvidia-smi --query-gpu=index,timestamp,power.draw,clocks.sm,clocks.mem,clocks.gr --format=csv -lms 10