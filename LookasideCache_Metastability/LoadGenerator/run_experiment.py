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

num_seconds = len(stats_data)                 
avg_cache_hit_rate_before_trigger = calculate_avg_hit_rate(0,15, stats_data)            
avg_cache_hit_rate_during_trigger = calculate_avg_hit_rate(15,20, stats_data)
avg_cache_hit_rate_after_trigger = calculate_avg_hit_rate(20,num_seconds, stats_data)

time_point_x = 20 
time_point_y = num_seconds - 2
cache_hit_at_point_x = stats_data[time_point_x][1]/stats_data[time_point_x][0]
cache_hit_at_point_y = stats_data[time_point_y][1]/stats_data[time_point_y][0]
slope = (cache_hit_at_point_y - cache_hit_at_point_x) / (time_point_y - time_point_x)    

print("slope of line: " + str(slope))
print("average cache hit rate before trigger: " + str(avg_cache_hit_rate_before_trigger))
print("average cache hit rate during trigger: " + str(avg_cache_hit_rate_during_trigger))
print("average cache hit rate after trigger: " + str(avg_cache_hit_rate_after_trigger))

difference_cache_hit_rate = avg_cache_hit_rate_after_trigger - avg_cache_hit_rate_before_trigger

has_metastable_issue_occured = 0
expected_cache_hit_rate_w_trigger = avg_cache_hit_rate_after_trigger + 3000 * slope  

#  if( difference_cache_hit_rate < 0.1 and slope < .001):
#      has_metastable_issue_occured = 1
    
# metastable_stats_array.append( (_lambda, trigger_size, has_metastable_issue_occured) )

# step 9: generate overall plot
# gather data (arrival_rate, trigger_size, failure_status)

arrival_rates_array = []
trigger_sizes_array = []        
meta_stable_issue_array = []

for item in metastable_stats_array:
    arrival_rates_array.append(item[0])
    trigger_sizes_array.append(item[1])
    meta_stable_issue_array.append(item[2])

fig = plt.figure(figsize=(8,8))
fig.suptitle('Metastable Issue Generation', fontsize=20)
plt.xlabel('Arrival rate', fontsize=14)
plt.ylabel('Trigger size', fontsize=14)
plt.scatter( arrival_rates_array, trigger_sizes_array, c= meta_stable_issue_array, cmap=matplotlib.colors.ListedColormap(colors))

experiment_plots_directory = "experiment_plots"
today_date_time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
file_with_image_extension = "test_at{}.png".format(today_date_time) 
experiment_plot_image_path = os.path.join(experiment_plots_directory, file_with_image_extension) # combining file name with directory
plt.savefig( experiment_plot_image_path, bbox_inches='tight')
print("\n\n--------------------------------------") 
 