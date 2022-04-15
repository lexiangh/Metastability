#!/usr/bin/python3
import pandas as pd
import sys
import pdb
import math
from enum import Enum

TIME_WINDOW = 1000 #in ms

#event types
class E(Enum):
    arrival = 1
    start = 2
    completion = 3

def analyze_job_table(job_tbl_path: str)->pd.DataFrame:
    job_df = pd.read_csv(job_tbl_path)

    job_stats = {'timestamp':[], 'qlen':[], 'latency':[]}

    #event driven programming: calculating qlen at each timestamp
    arrival_df = job_df[['arrival_uptime']].copy()                                                                                                
    arrival_df['event_type'] = E.arrival.value                                                                                                    
    arrival_df.rename(columns={'arrival_uptime': 't'}, inplace = True)                                                                            

    completion_df = job_df[['completion_uptime']].copy()                                                                                          
    completion_df['event_type'] = E.completion.value                                                                                              
    completion_df.rename(columns={'completion_uptime': 't'}, inplace = True)                                                                      

    events_df = pd.concat([arrival_df, completion_df])                                                                                    
    events_df.sort_values(by=['t'], inplace = True)                                                                                               
    events_df = events_df[events_df['t'] > 0]  
    
    rps_stats = {'timestamp':[], 'rps':[]}
    #calculate arrival_rate
    arrival_uptime_df = job_df[['arrival_uptime']].copy()
    arrival_uptime_sorted = job_df.sort_values(by=['arrival_uptime'])

    curr_ts = 0
    accu_num_reqs = 0
    for index, row in arrival_uptime_df.iterrows():
        if curr_ts < math.floor(row['arrival_uptime']/TIME_WINDOW):
            rps_stats['timestamp'].append(curr_ts)
            rps_stats['rps'].append(accu_num_reqs)
            accu_num_reqs = 0
            curr_ts = math.floor(row['arrival_uptime']/TIME_WINDOW)
        accu_num_reqs += 1

    #calculate qlen using arrival_uptime and completion_uptime                                                                                         
    curr_ts = 0                                                                                                                                       
    curr_qlen = 0                                                                                                                                     
    for index, row in events_df.iterrows():                                                                                                           
        curr_ts = math.floor(row['t']/TIME_WINDOW)                                                                                                    
        if curr_ts not in job_stats['timestamp']:                                                                                                     
            job_stats['timestamp'].append(curr_ts)                                                                                                    
            job_stats['qlen'].append(curr_qlen)                                                                                                       
        if row['event_type'] == E.arrival.value:                                                                                                      
            curr_qlen += 1                                                                                                                            
        elif row['event_type'] == E.completion.value:                                                                                                 
            curr_qlen -= 1                                                                                                                            
        else:                                                                                                                                         
            print(f"Error! Unknown event type: {row['event_type']}")

    #calculate latency
    job_df_sorted_by_completion = job_df.sort_values(by=['completion_uptime'])
    curr_ts = 0
    completed_job_counts = 0
    accumulated_latency = 0
    for index, row in job_df_sorted_by_completion.iterrows():
        if curr_ts < math.floor(row['completion_uptime']/TIME_WINDOW):
            job_stats['latency'].append(accumulated_latency/completed_job_counts if completed_job_counts>0 else 0)
            accumulated_latency = 0
            completed_job_counts = 0
            curr_ts = math.floor(row['completion_uptime']/TIME_WINDOW)
            assert curr_ts in job_stats['timestamp'], f'Error! curr_ts: {curr_ts} not in job_stats'
        if row['completion_t'] > 0:
            completed_job_counts += 1
            accumulated_latency += (row['completion_t'] - row['arrival_t'])

    min_len = min(len(job_stats['timestamp']), len(job_stats['qlen']), len(job_stats['latency']))
    job_stats['timestamp'] = job_stats['timestamp'][:min_len]
    job_stats['qlen'] = job_stats['qlen'][:min_len]
    job_stats['latency'] = job_stats['latency'][:min_len]

    job_stats_df = pd.DataFrame(job_stats)
    job_stats_df['latency'] = (job_stats_df['latency']/1e6).round(3) #in ms
    job_stats_df.rename(columns={'latency': 'latency_ms'}, inplace = True)

    rps_stats_df = pd.DataFrame(rps_stats)
    merged_df = job_stats_df.merge(rps_stats_df, on='timestamp', how='outer')
    return merged_df
    
def analyze_gcutil_table(gcutil_tbl_path: str)->pd.DataFrame:
    df = pd.read_csv(gcutil_tbl_path, delim_whitespace=True)
    gc_stats ={'timestamp':[], 'S0':[], 'S1':[], 'E':[], 'O':[], 'M':[], 'YGC':[], 'YGCT':[], 'FGC':[], 'FGCT':[], 'GCT':[]}
    last_YGC = 0
    last_YGCT = 0
    last_FGC = 0
    last_FGCT = 0
    last_GCT = 0
    for index, row in df.iterrows():
        if row['Timestamp'] == int(row['Timestamp']): #TODO: deal with possible cases of missing data
            gc_stats['timestamp'].append(row['Timestamp'])
            gc_stats['S0'].append(row['S0'])
            gc_stats['S1'].append(row['S1'])
            gc_stats['E'].append(row['E'])
            gc_stats['O'].append(row['O'])
            gc_stats['M'].append(row['M'])
            gc_stats['YGC'].append(row['YGC'] - last_YGC)
            last_YGC = row['YGC']
            gc_stats['YGCT'].append(row['YGCT'] - last_YGCT)
            last_YGCT = row['YGCT']
            gc_stats['FGC'].append(row['FGC'] - last_FGC)
            last_FGC = row['FGC']
            gc_stats['FGCT'].append(row['FGCT'] - last_FGCT)
            last_FGCT = row['FGCT']
            gc_stats['GCT'].append(row['GCT'] - last_GCT)
            last_GCT = row['GCT']
            
    gc_stats_df = pd.DataFrame(gc_stats)
    gc_stats_df['timestamp'] = gc_stats_df['timestamp'].astype('int64')
    gc_stats_df['YGCT'] = (1000*gc_stats_df['YGCT']).round(1) #in ms
    gc_stats_df['FGCT'] = (1000*gc_stats_df['FGCT']).round(1) #in ms
    gc_stats_df['GCT'] = (1000*gc_stats_df['GCT']).round(1) #in ms
    
    return gc_stats_df
    
def main():
    job_tbl_path = ''
    gc_tbl_path = ''
    
    if len(sys.argv) != 3:
        print(f"Please give a job table and a GC table:")
        sys.exit(0)        
    else:
        job_tbl_path = sys.argv[1]
        gc_tbl_path = sys.argv[2]

    job_df = analyze_job_table(job_tbl_path)
    gc_df = analyze_gcutil_table(gc_tbl_path)
    measurement_df = pd.merge(job_df, gc_df, how='right')

    measurement_df.to_csv('measurement.csv', index=False)
    
if __name__=="__main__":
    main()
