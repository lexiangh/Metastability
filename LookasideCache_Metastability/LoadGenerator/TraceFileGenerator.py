# import exponential
import numpy as np
from scipy.stats import zipf 
import math
import random
import sys
import os.path
import numpy as np 
import collections

row_nums_in_db = 2827946
print("TraceFileGenerator: parameters: " + str(sys.argv[1:]))

# command line arguments 
arrival_rate_parameter = float(sys.argv[1:][0])
alpha= float(sys.argv[1:][1]) 
duration_of_test = int(sys.argv[1:][2])


number_of_arrivals = int(arrival_rate_parameter * duration_of_test) 
request_types =  np.zeros(number_of_arrivals).astype(int)
job_size_rate_parameter = 100

f_name = "traces/trace_file_" + str(arrival_rate_parameter) + "_" + str(alpha) +".txt"
f = open(f_name, "w+")

scale_arrival = 1/arrival_rate_parameter
interarrival_times = np.random.exponential(scale_arrival, number_of_arrivals)
arrival_times = np.cumsum(interarrival_times)

scale_jobsize = 1/job_size_rate_parameter
job_sizes = np.random.exponential(scale_jobsize, number_of_arrivals).astype(int)
#print(job_sizes)

# zipf distribution for generating load 
zipf_rand_num_iter = 0
job_types = np.zeros(number_of_arrivals)

while(zipf_rand_num_iter!= number_of_arrivals):
    new_zipf_value = np.random.zipf(alpha) 
    if(new_zipf_value>0 and new_zipf_value<=row_nums_in_db):
        job_types[zipf_rand_num_iter] = new_zipf_value
        zipf_rand_num_iter+=1 
        
#  job_types_unscaled =  np.random.zipf(alpha, number_of_arrivals) #zipf.rvs(alpha, size = number_of_arrivals)
job_types = job_types.astype(int) #(job_types_unscaled/float(max(job_types_unscaled)))*1000
#print(min(job_types)) 
#print(max(job_types))


for i in range(0, number_of_arrivals):
    string = str(arrival_times[i]) + " " + str(request_types[i]) + " " + str(job_sizes[i]) + " " + str(job_types[i]) + "\n"
    f.write(string)
f.close()

 
counter=collections.Counter(job_types) 
iter = 0 
sum = 0

for i in counter.keys():
    if(iter == 2000000):
        break
    #print(str(iter+1) + " " + str(counter[iter+1]/number_of_arrivals))
    sum+= counter[iter+1]
    iter+=1
print(sum/number_of_arrivals)
 