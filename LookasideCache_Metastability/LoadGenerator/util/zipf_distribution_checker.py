import math
import sys
 

args_len = len(sys.argv[1:])

if(args_len != 2):        
        print("enter valid parameter, provide trace file name, num of entries")
        exit()
    
file_name = sys.argv[1:][0]
N = int(sys.argv[1:][1])

frequency={}
distribution = []
total_entries = 0


with open(file_name) as file:
    for line in file:
        split_line = line.split(" ")
        stripped = [s.strip() for s in split_line] 
        job_type = int(stripped[3])
        
        if(job_type in frequency):
                frequency[job_type]+=1
        else:
                frequency[job_type] = 1
        total_entries+=1
            
for item in frequency:
        distribution.append( (item, frequency[item]/total_entries) ) 

distribution.sort(key=lambda x:x[1], reverse = True)
 
sum_first_N_entries = 0

for i in range(N):
        #print( str(distribution[i][0]) + " " + str(distribution[i][1]))
        sum_first_N_entries+= distribution[i][1]
        
print('first ' + str(N) + ' entries: ' + str(sum_first_N_entries))