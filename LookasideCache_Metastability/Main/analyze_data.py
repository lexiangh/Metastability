import os 
from os import listdir
from os.path import isfile, join
import math 
import numpy as np
import sys
from datetime import datetime
import time



if(len(sys.argv[1:][0] !=1))
    print("Please pass data directory. e.g: single_test, timeout1/2 or alpha1/2")
    quit()

results_directory =  sys.argv[1:][0]

all_result_files = [f for f in listdir(results_directory) if isfile(join(results_directory, f))]


for result_file in all_result_files:
    split_line = result_file.split("_")
    arrival_rate = split_line[1]
    zipf_alpha = split_line[2]
    duration = split_line[4]
    trigger_size = split_line[6]
    timeout= split_line[8].replace(".txt",'')
    print(arrival_rate + " " +  zipf_alpha + " " + duration + " " + trigger_size)
    file_full_path = results_directory + "/" + result_file
    cmd_str = f"python3 generate_system_behaviour_plot.py {file_full_path} {arrival_rate} {zipf_alpha} {duration} {trigger_size} {timeout} {testtype}"
    with open(file_full_path) as file:
        os.system(cmd_str)
        
