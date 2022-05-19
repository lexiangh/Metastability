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
load= int(sys.argv[1:][0])
trigger= int(sys.argv[1:][1])
duration_of_test=int(sys.argv[1:][2])
zipf_parameter=float(sys.argv[1:][3])
num_threads=int(sys.argv[1:][4])
sleep_period_before_trigger=int(sys.argv[1:][5])
timeout=int(sys.argv[1:][7])
test_type = sys.argv[1:][8]

if(sys.argv[1:][6] == "False"):
    closed_loop_test= False
else:
    closed_loop_test = True 

args_len = len(sys.argv[1:])

if(args_len != 9):        
        print("enter valid parameters:  load, trigger, duration of test, zipf_param, num_threads, trigger_offset, closed_loop_test")
        exit()

def run_trace_replay(_trace_file_name, _num_threads, _result_file_name):
    os.system("make") # to make sure latest changes are being used 
    run_TraceReplay_command = "./TraceReplay -t {}  {} -n {} -r {}".format(_trace_file_name, closed_loop_flag, _num_threads, _result_file_name)
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
if(closed_loop_test):
    closed_loop_flag = " -c"
else:
    closed_loop_flag = ""  
# config for connecting to memcached server VM
user = "ubuntu"
memcached_host = "172.31.1.84" # memcached server
master_vm = "172.31.27.60"
memcached_VM_command = "python3 warm_up_cache.py"
path_to_rsa_key = "cache_workers.pem"
"""
 trigger size == -1 denotes a flush_all
  and 
 trigger size == 0 means no trigger, we would expect stable behaviour
"""
# configs for experiment 
#zipf_parameter = 1.00001   
metastable_stats_array = []

# trace replay config  
result_file_name = "results_warm_cache/result_300.0.1.00001.txt"
trace_file_name  = "traces/trace_file_300.0_1.00001.txt"
 

#plotting config
colors = ['green', 'red'] # red == metastable, green = not metastable 


_lambda = load
trigger_size = trigger

print("\n\n--------------------------------------\n\n")
print("testing with lambda = " + str(_lambda))

# step 1: warm up cache
try:
    cmd = f"ssh -o StrictHostKeyChecking=no -i {path_to_rsa_key} -p 22 {user}@{memcached_host} \"{memcached_VM_command}\"" 
    out = subprocess.check_output(cmd , shell= True)
    print(out)
except subprocess.CalledProcessError as e:
    print("error when warming up cache")
    pass

# step 2: generate a new trace, we want new traces even for same config (to reduce bias)  
generate_trace_command = 'python3 TraceFileGenerator.py ' + str(_lambda) + ' ' + str(zipf_parameter) + ' ' + str(duration_of_test)
os.system(generate_trace_command)

# step 3: run the TraceReplay (using & making the process non blocking) 
trace_file_name = "traces/trace_file_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) +".txt"
results_directory = "results_warm_cache/" 
result_file_name = "result_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) + "_DUR_" + str(duration_of_test) + "_TRSZ_" + str(trigger_size) + "_TMOUT_"+ str(timeout) +".txt"
result_file_path = results_directory + result_file_name
trace_replay_thread = Thread(target= run_trace_replay, args=(trace_file_name, num_threads, result_file_path,))
trace_replay_thread.start()  

# step 4: sleep for 10 s, then run trigger 
time.sleep(sleep_period_before_trigger)

# step 5: run trigger  
trigger_command = "python3 trigger_size_k.py " + str(trigger_size)

for _t in range(0,5):
    os.system(trigger_command) 


# step 6: wait for TraceReplay to finish
trace_replay_thread.join()  

# step 7: process result file to generate file with cache_hit_rate 
# call stats only after experiment has finished
process_stats_command = "python3 collect_stats_over_time.py {} {} {} {} {}".format(result_file_path, _lambda, zipf_parameter, trigger_size,duration_of_test)
os.system(process_stats_command)

os_command = f"ssh-keyscan {memcached_host}  >> $HOME/.ssh/known_hosts"
#os_command = f"ssh-keyscan {master_vm}  >> $HOME/.ssh/known_hosts"

try:
    # Set scp and ssh data.
    connUser = 'ubuntu'
    connHost = master_vm
    connPath = '/home/ubuntu/Cache_Experiments/Main/' + test_type + "/" + result_file_name  
    #os_command = f"ssh-keyscan {master_vm}  >> $HOME/.ssh/known_hosts"
    #os.system(os_command)
    # Use scp to send file from local to host.
    scp_command = "sudo sshpass -p metastability scp -o StrictHostKeyChecking=no " +  result_file_path + " {}@{}:{}".format(connUser, connHost, connPath)
    #scp = subprocess.Popen(['scp', '-i', connPrivateKey, result_file_path, '{}@{}:{}'.format(connUser, connHost, connPath)])
    os.system(scp_command)
except CalledProcessError:
    print('ERROR: Connection to host failed!')
