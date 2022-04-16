
import os 
from os import listdir
from os.path import isfile, join
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
from datetime import datetime
import time

def extract_int(read):
    
    if(len(read) == 1 and read[0] == '0'):
        return 0
    
    #print(read)
    last_char = read[len(read)-1]
    #print(last_char)
    read_minus_last_char = read[0 : len(read) -1]
    read_int = int(read_minus_last_char)
    #print(read_minus_last_char)
    
    if(last_char == 'k'):
        read_int = read_int/1024
    elif(last_char == 'B'):
        read_int = (read_int/1024)/1024
    return read_int

stats_per_arival = []

arrivals  = [7 , 14, 21, 28, 35, 42, 49, 56, 63]
for i in arrivals:
    file_name = f"arr_{i}_data.txt"
    print(file_name)
    with open(file_name) as file:   
        
        usr_avg = 0
        sys_avg = 0
        idle_avg = 0
        stl_avg = 0
        not_idle_avg = 0
        
        read_avg = 0
        write_avg = 0
        
        recv_avg = 0
        send_avg = 0
              
        for line in file:
            split_line = line.split()
            stripped = [s.strip() for s in split_line] 
            #print(stripped)
            usr = int(stripped[0])
            sys = int(stripped[1])
            idle = int(stripped[2])
            stl = int(stripped[3])
            #print(idle)
            not_idle = 100 - idle 
            #print(not_idle)
            usr_avg+= usr
            sys_avg += sys
            idle += idle 
            stl += stl 
            not_idle_avg += not_idle
            
            read = stripped[5]
            read_int = extract_int(read)
            #print(read_int)
            read_avg+= read_int
            
            write = stripped[6] 
            write_int = extract_int(write)
            #print(write_int)
            write_avg+= write_int
            
            send = stripped[8] 
            send_int = extract_int(send)
            #print(send_int)
            send_avg+= send_int
            # usr sys idl wai stl| read  writ| recv  send
            #print(str(usr) + " " + str(sys) + " " + str(idle) + " " + str(stl)+ " " + read + " " + write + " " + send )
        
        stats_per_arival.append( ( (not_idle_avg/60)/100, ((read_avg/60)/ 362), (send_avg/60)/24.5))
        
for i in range(0, len(arrivals)):
    print(str(stats_per_arival[i][0]) + ", " + str(stats_per_arival[i][1]) + ", " + str(stats_per_arival[i][2]))