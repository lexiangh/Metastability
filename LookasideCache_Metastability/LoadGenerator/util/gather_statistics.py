import os 
from os import listdir
from os.path import isfile, join
import subprocess

traces_directory = "traces"
results_directory = "results_warm_cache"

file_names = [f for f in listdir(traces_directory) if isfile(join(traces_directory, f))]
num_files = len(file_names)

for i in range(0, num_files):
    file_name = file_names[i]
    file_name = file_name.replace(".txt", "")
    result_file_name = file_name + "_result" + ".txt"
    split_name = file_name.split("_")
    arrival_rate = float(split_name[2])
    alpha = float( split_name[3])
    print("\n\n\n-------------------------------------------------------------")
    print("arrival rate: " +  str(arrival_rate) + " alpha: " + str(alpha))
    command = "./TraceReplay -t " + join(traces_directory, file_names[i]) + " -r " + join(results_directory, result_file_name)
    os.system(command) 
    print("\n\n\n-------------------------------------------------------------")
 
 