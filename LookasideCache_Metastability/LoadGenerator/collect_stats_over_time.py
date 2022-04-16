import os 
from os import listdir
from os.path import isfile, join
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime
import time

kill_timeout_for_php = 1
# helper functions

def plot_data( x_points, y_points, file_with_image_extension):
    f, ax = plt.subplots(1)
    plt.plot(x_points, y_points)
    # plt.plot(time_points, latency_points)
    ax.set_ylim(ymin=0) 

    
    image_directory = "result_plots"
    current_directory = os.getcwd()
    final_image_directory = os.path.join(current_directory, r'result_plots')

    if not os.path.exists(final_image_directory):
        os.makedirs(final_image_directory)   

    image_file_path = join(image_directory, file_with_image_extension) # combining file name with directory
    plt.savefig( image_file_path, bbox_inches='tight')

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def plot_multiple_data( x_points, y_points1, y_points2, y_points3, file_with_image_extension):
   # f, ax = plt.subplots()
   # plt.plot(x_points, y_points)
    # plt.plot(time_points, latency_points)
    #ax.set_ylim(ymin=0) 
    fig, ax1 = plt.subplots()
    
    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('latency(ns)', color='black')
    ax1.plot(x_points, y_points1, color=color, linewidth = 2 , alpha= 0.6, label = "latency")
    ax1.tick_params(axis='y', labelcolor='black')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('hit rate/error rate', color='black')  # we already handled the x-label with ax1
    ax2.plot(x_points, y_points2, color=color, linewidth = 2, alpha= 0.6, label = "cache hit rate")
    color = 'tab:orange'
    ax2.plot(x_points, y_points3, '--', color=color, linewidth = 2, alpha= 0.6, label = "error rate")
    ax2.set_ylim(ymin = 0, ymax = 1)
    # plt.arrow(x=10, y=0, dx=0, dy=5, width=.08, facecolor='red')
    ax2.tick_params(axis='y', labelcolor='black')
    fig.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
     
    image_directory = "result_plots"
    current_directory = os.getcwd()
    final_image_directory = os.path.join(current_directory, r'result_plots')

    if not os.path.exists(final_image_directory):
        os.makedirs(final_image_directory)   

    image_file_path = join(image_directory, file_with_image_extension) # combining file name with directory
    plt.savefig( image_file_path, bbox_inches='tight')


## helper functions end





args_len = len(sys.argv[1:])

if(args_len != 5):        
        print("enter valid parameter, provide absolute file path for resultFile from TraceReplay, arrival_rate, trigger_size, test_duration")
        exit()
    
file_name = sys.argv[1:][0]
arrival_rate = sys.argv[1:][1]
alpha = sys.argv[1:][2]
trigger_size = sys.argv[1:][3]
test_duration = sys.argv[1:][4]

ns_in_a_sec = 1000000000  
num_seconds = -1
hit_rates = [0] * 100000 # upper bound , assuuming experiment goes on for 1000 seconds
error_rates = [0] * 100000
job_completions = [0] * 100000
latency_per_second = [0] * 100000
    
with open(file_name) as file:
    first_line = file.readline()
    first_line = first_line.strip()
    experiment_start_time = int(first_line)
    for line in file:
        split_line = line.split(" ")
        stripped = [s.strip() for s in split_line]
        start_time = int(stripped[0])
        duration = int(stripped[1])
        end_time = (start_time + duration) - experiment_start_time
        cache_hits = int(stripped[2])
        errors = int(stripped[3])
        
        t_th_second = math.ceil(end_time/ns_in_a_sec)
        num_seconds = max( num_seconds , t_th_second) 
        hit_rates[ t_th_second ] += cache_hits # cache_hits will be either 0 or 1
        error_rates[ t_th_second ] += errors # error will be either 0 or 1
        job_completions[ t_th_second ]+= 1 # as each entry correspond to a job completion     
        latency_per_second[t_th_second]+=duration

hit_rates = hit_rates[0: num_seconds+1]
error_rates = error_rates[0: num_seconds+1]
latency_per_second = latency_per_second[0: num_seconds +1]
time_points = [0] * (num_seconds + 1)



current_directory = os.getcwd()
stats_directory = "result_stats"
final_stats_directory = os.path.join(current_directory, r'result_stats')

if not os.path.exists(final_stats_directory):
   os.makedirs(final_stats_directory)
stats_file_name = "STATS_ARV_RATE_{}_ALPHA_{}_TSZ_{}_DUR_{}.txt".format(arrival_rate, alpha, trigger_size, test_duration) 
stats_file_path = os.path.join( final_stats_directory, stats_file_name)

stats_file = open(stats_file_path, "w") 
for k in range(0, num_seconds + 1):
    stats_file.write( str(job_completions[k]) + " " +  str(hit_rates[k]) + " " + str(error_rates[k]) + "\n")


for j in range (0, num_seconds+1): 
    if(job_completions[j]!= 0):
        hit_rates[j]/= job_completions[j]
        error_rates[j]/= job_completions[j]
        latency_per_second[j]/= job_completions[j]
    time_points[j] = j 

# print("max cache hit rate: " + str(max( hit_rates)))
# print("max cache hit rate index : " + str(hit_rates.index(max(hit_rates))))
# print("job completions : " + str(job_completions[1]))

hit_rate_points  = np.array( hit_rates)
error_rate_points = np.array( error_rates)
time_points = np.array(time_points)
latency_points = np.array(latency_per_second)
today_date_time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
H_file_with_image_extension =  f"H_IMG_ARV_RATE_{arrival_rate}_ALPHA_{alpha}_TSZ_{trigger_size}_DUR_{test_duration}_{today_date_time}_TO_{kill_timeout_for_php}.png"   
L_file_with_image_extension =  f"L_IMG_ARV_RATE_{arrival_rate}_ALPHA_{alpha}_TSZ_{trigger_size}_DUR_{test_duration}_{today_date_time}_TO_{kill_timeout_for_php}.png"   
E_file_with_image_extension =  f"E_IMG_ARV_RATE_{arrival_rate}_ALPHA_{alpha}_TSZ_{trigger_size}_DUR_{test_duration}_{today_date_time}_TO_{kill_timeout_for_php}.png"   
C_file_with_image_extension = f"C_IMG_ARV_RATE_{arrival_rate}_ALPHA_{alpha}_TSZ_{trigger_size}_DUR_{test_duration}_{today_date_time}_TO_{kill_timeout_for_php}.png"
plot_data(time_points, hit_rate_points, H_file_with_image_extension)
plot_data(time_points, error_rate_points, E_file_with_image_extension)
plot_data(time_points, latency_points, L_file_with_image_extension)
plot_multiple_data(time_points, latency_points, hit_rate_points, error_rate_points, C_file_with_image_extension)
# store completions cache_hit_rate error_rate 

