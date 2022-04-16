import os
values_close_to_one = [1.01, 1.001]
values_far_from_one = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0] 

zipf_size_1 = len(values_close_to_one)
zipf_size_2 = len(values_far_from_one)
number_of_different_arrival_rate = 15 # each arrival rate differs by 250
duration_of_test = 30 # in seconds

for i in range(0, zipf_size_1):
    first_arrival_rate = 1000
    for j in range(10, number_of_different_arrival_rate+1):
        command = 'python3 TraceFileGenerator.py ' + str(first_arrival_rate * j) + ' ' + str(values_close_to_one[i]) + ' ' + str(duration_of_test)
        print(command)
        os.system(command)

"""
for i in range(0, zipf_size_2):
    first_arrival_rate = 250
    for j in range(1, number_of_different_arrival_rate+1):
        command = 'python3 TraceFileGenerator.py ' + str(first_arrival_rate* j) + ' ' + str(values_far_from_one[i])
        print(command)
        os.system(command)
"""