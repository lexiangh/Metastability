import os 
from os import listdir
from os.path import isfile, join
import math
import sys
import subprocess
from threading import Thread
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# config for connecting to memcached server VM
user = "ubuntu"
host = "10.158.50.15" # memcached server
memcached_VM_command = "python3 warm_up_cache.py"
path_to_rsa_key = "newIdentity.key"



"""
 trigger size == -1 denotes a flush_all
  and 
 trigger size == 0 means no trigger, we would expect stable behaviour
"""
# configs for experiment 
zipf_parameter = 1.00001
duration_of_test =  32 
sleep_period_before_trigger = 15 # seconds  # because trace replay sleeps for 5 second to start with
metastable_stats_array = []


# trace replay config 
num_threads = 192
result_file_name = "results_warm_cache/result_300.0.1.00001.txt"
trace_file_name  = "traces/trace_file_300.0_1.00001.txt"


#plotting config
colors = ['green', 'red'] # red == metastable, green = not metastable 

#open / closed loop test config
closed_loop_test = False
if(closed_loop_test):
    closed_loop_flag = " -c"
else:
    closed_loop_flag = "" 


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
    

def plot_data( x_points, y_points, file_with_image_extension):
    f, ax = plt.subplots(1)
    plt.plot(x_points, y_points)
    # plt.plot(time_points, latency_points)
    ax.set_ylim(ymin=0) 
    
    z_points = np.polyfit(x_points, y_points, 2)
    p = np.poly1d(z_points)
    plt.plot(x_points,p(x_points),"r--")
    
    image_directory = "trend_line_plots"
    current_directory = os.getcwd()
    final_image_directory = os.path.join(current_directory, r'trend_line_plots')

    if not os.path.exists(final_image_directory):
        os.makedirs(final_image_directory)   

    image_file_path = join(image_directory, file_with_image_extension) # combining file name with directory
    plt.savefig( image_file_path, bbox_inches='tight')


    
max_trigger_size = 2000000
min_trigger_size = 1
arrival_trigger_size_arr = []


for _lambda in range(420, 421, 60):
    left = min_trigger_size
    right = max_trigger_size
    best_trigger_size = max_trigger_size
    
    print("\n\n--------------------------------------\n\n")
    print("testing with lambda = " + str(_lambda))

    while left < right and right > 0: 
        
        trigger_size = int( (left + right )/2 )
                
        print("testing with trigger_size = " + str(trigger_size))
            
        # step 1: warm up cache
        try:
            out = subprocess.check_output(["ssh", "-i", path_to_rsa_key, "-p", "22", "{}@{}".format(user, host), memcached_VM_command])
            print(out)
        except subprocess.CalledProcessError as e:
            print("error when warming up cache")
            pass
        
        # step 2: generate a new trace, we want new traces even for same config (to reduce bias)  
        generate_trace_command = 'python3 TraceFileGenerator.py ' + str(_lambda) + ' ' + str(zipf_parameter) + ' ' + str(duration_of_test)
        os.system(generate_trace_command)
        
        # step 3: run the TraceReplay (using & making the process non blocking) 
        trace_file_name = "traces/trace_file_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) +".txt"
        result_file_name = "results_warm_cache/result_" + str(float(_lambda)) + "_" + str(float(zipf_parameter)) +".txt"
 
        trace_replay_thread = Thread(target= run_trace_replay, args=(trace_file_name, num_threads, result_file_name,))
        trace_replay_thread.start()  

        # step 4: sleep for 10 s, then run trigger 
        time.sleep(sleep_period_before_trigger)

        # step 5: run trigger  
        trigger_command = "python3 trigger_size_k.py " + str(trigger_size)
    
        for _t in range(0,3):
            os.system(trigger_command)
            time.sleep(1)
                
        # step 6: wait for TraceReplay to finish
        trace_replay_thread.join()  
        
        # step 7: process result file to generate file with cache_hit_rate 
        # call stats only after experiment has finished
       
        process_stats_command = "python3 collect_stats_over_time.py {} {} {} {}".format(result_file_name, _lambda, trigger_size,duration_of_test)
        os.system(process_stats_command)
      

        # step 8: decide whether metastable issue occured or not based on cache hit rate over time
            # step 8.1 : grab stats file
            # step 8.2 pick cache hit rate from two distant points in time (after the trigger, after 10 seconds) (currently testing 12th second -- last second)
            # step 8.3: decide whether metastable issue occured or not, by using the a simple trend line
    
        stats_file_name = "STATS_ARV_RATE_{}_TSZ_{}_DUR_{}.txt".format(_lambda, trigger_size, duration_of_test)
        stats_directory = "result_stats"
        stats_file_path = os.path.join( stats_directory, stats_file_name)  
        stats_data = []
        cache_hit_rates = []
        time_arr = []
        
        
        with open(stats_file_path) as file:
            for line in file:
                line = line.rstrip()
                data = line.split(" ")
                data_tuple = ( int(data[0]), float(data[1]), float(data[2])) 
                # [0] -> compleitions [1]-> cache hit rate [2] -> error rate
                stats_data.append(data_tuple)
                
                if(float(data[0]) != 0 ):
                    cache_hit_rates.append(float(data[1])/float(data[0]))
                else:
                    cache_hit_rates.append(0)
               
        num_seconds = len(stats_data)                 
        avg_cache_hit_rate_before_trigger = calculate_avg_hit_rate(0,8, stats_data)            
        avg_cache_hit_rate_during_trigger = calculate_avg_hit_rate(8,20, stats_data)
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
        
        cache_hit_rates_after_trigger = cache_hit_rates[ 20 : ]
        time_length = len(cache_hit_rates_after_trigger)
       
        time_values = []
        for t in range(0, time_length):
            time_values.append(t)
        
        
        time_point_1hr = 3000                 
       # a , b , c = np.polyfit(time_values, cache_hit_rates_after_trigger, deg=2)
       # predicted_cache_hit_rate = np.polyval([a,b,c], time_point_1hr)
       #print("predicted cache hit rate: " + str(predicted_cache_hit_rate))       
        f = np.polyfit(time_values, cache_hit_rates_after_trigger, deg= 1)
        print("predicted slope: " + str(predicted_cache_hit_rate))
        plot_data(time_values, cache_hit_rates_after_trigger, "tmp_trend_plt_" + str(_lambda)  + "_" + str(trigger_size) + ".png")
        difference_cache_hit_rate = avg_cache_hit_rate_after_trigger - avg_cache_hit_rate_before_trigger

        has_metastable_issue_occured = 0
        expected_cache_hit_rate_w_trigger = cache_hit_at_point_y + 3000 * slope  
        
        print("expected cache hit rit w trigger after an hour: " + str(expected_cache_hit_rate_w_trigger))
        
        #if(expected_cache_hit_rate_w_trigger > 0.9 * expected_cache_hit_rate_wo_trigger):
         #   has_metastable_issue_occured = 1
        if avg_cache_hit_rate_before_trigger - avg_cache_hit_rate_before_trigger > 0.5:
            has_metastable_issue_occured = 1
        
        if(has_metastable_issue_occured == 1):
            metastable_stats_array.append( (_lambda, trigger_size, has_metastable_issue_occured))
            best_trigger_size = min(best_trigger_size, trigger_size)
            right = trigger_size - 1000
        else:
            left = trigger_size + 1000
            
        print("trgz sz = " + str(trigger_size) + " metastable ? " + str(has_metastable_issue_occured))
      #  if( difference_cache_hit_rate < 0.1 and slope < .001):
      #      has_metastable_issue_occured = 1
    arrival_trigger_size_arr.push((_lambda, best_trigger_size))        


for i in len(arrival_trigger_size_arr):
    print("arrival rate ->" +  str(arrival_trigger_size_arr[0]) + " , trigger sz ->" + str(arrival_trigger_size_arr[1]))

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
 