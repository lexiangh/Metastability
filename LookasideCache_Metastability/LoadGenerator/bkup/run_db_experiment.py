import os 
import math
import sys
import subprocess
from threading import Thread
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from math import sqrt 

# helper functions 

def run_trace_replay(_trace_file_name, _num_threads, _result_file_name):
    run_TraceReplay_command = "./TraceReplay -t {}  -n {} -r {}".format(_trace_file_name, _num_threads, _result_file_name) +  closed_loop_flag
    os.system(run_TraceReplay_command)  


def calculate_avg_hit_rate(start, end, stats_data):
    cache_hits = 0
    job_completitions = 0
        
    for t in range(start, end):
        cache_hits+= stats_data[t][1]
        job_completitions+= stats_data[t][0]
        
    avg_cache_hit_rate = cache_hits/job_completitions
    return avg_cache_hit_rate
    

#open / closed loop test config
closed_loop_test = False
if(closed_loop_test):
    closed_loop_flag = " -c"
else:
    closed_loop_flag = "" 
        
# config for connecting to memcached server VM
user = "ubuntu"
host = "10.158.4.23" # memcached server
memcached_VM_command = "python3 warm_up_cache.py"
path_to_rsa_key = "newIdentity.key"
"""
 trigger size == -1 denotes a flush_all
  and 
 trigger size == 0 means no trigger, we would expect stable behaviour
"""
# configs for experiment 
zipf_parameter = 1.00001
#zipf_parameter = 1.14165
duration_of_test =  120      #3600 # 1 *  60 * 60 
sleep_period_before_trigger = 15 # 15 # seconds  # because trace replay sleeps for 5 second to start with
metastable_stats_array = []

# trace replay config 
num_threads = 192  #192
result_file_name = "results_warm_cache/result_300.0.1.00001.txt"
trace_file_name  = "traces/trace_file_300.0_1.00001.txt"

#plotting config
colors = ['green', 'red'] # red == metastable, green = not metastable 


#lambda_trigger_arr = [ (150, -1 ), (180, -1), (210, 100000), (240, 100000), (270,100000 ),
#                     (300, 10000), (330, 10000)] 
 
lambda_trigger_arr = [   
                    #  (7, 0)
                     # (14, 0)
                    #  (21, 0)
                     # (28, 0)
                   #   (35, 0)
                    #  (42, 0)
                    #  (49, 0),
                    #  (56, 0),
                      (63,0)                          
                     ] 
   
for iter in range(0, len(lambda_trigger_arr)):
    _lambda = lambda_trigger_arr[iter][0]
    trigger_size = lambda_trigger_arr[iter][1]
    print("\n\n--------------------------------------\n\n")
    print("testing with lambda = " + str(_lambda))
        
    # step 2: generate a new trace, we want new traces even for same config (to reduce bias)  
    generate_trace_command = 'python3 TraceFileGenerator.py ' + str(_lambda) + ' ' + str(zipf_parameter) + ' ' + str(duration_of_test)
    os.system(generate_trace_command)
    
    # step 3: run the TraceReplay (using & making the process non blocking) 
    trace_file_name = "traces/trace_file_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) +".txt"
    result_file_name = "results_warm_cache/result_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) + "_DUR_" + str(duration_of_test) + "_TRSZ_" + str(trigger_size) +".txt"

    trace_replay_thread = Thread(target= run_trace_replay, args=(trace_file_name, num_threads, result_file_name,))
    trace_replay_thread.start()  

    
    # step 6: wait for TraceReplay to finish
    trace_replay_thread.join()  
    
    # step 7: process result file to generate file with cache_hit_rate 
    # call stats only after experiment has finished
    
    process_stats_command = "python3 collect_stats_over_time.py {} {} {} {} {}".format(result_file_name, _lambda, zipf_parameter, trigger_size,duration_of_test)
    os.system(process_stats_command)
    

    # step 8: decide whether metastable issue occured or not based on cache hit rate over time
        # step 8.1 : grab stats file
        # step 8.2 pick cache hit rate from two distant points in time (after the trigger, after 10 seconds) (currently testing 12th second -- last second)
        # step 8.3: decide whether metastable issue occured or not, by using the a simple trend line

    stats_file_name = "STATS_ARV_RATE_{}_ALPHA_{}_TSZ_{}_DUR_{}.txt".format(_lambda, zipf_parameter, trigger_size, duration_of_test)
    stats_directory = "result_stats"
    stats_file_path = os.path.join( stats_directory, stats_file_name)  
    stats_data = []
    with open(stats_file_path) as file:
        for line in file:
            line = line.rstrip()
            data = line.split(" ")
            data_tuple = ( int(data[0]), float(data[1]), float(data[2])) 
            # [0] -> compleitions [1]-> cache hit rate [2] -> error rate
            stats_data.append(data_tuple)
 