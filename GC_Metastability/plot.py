#!/usr/bin/python3
import pandas as pd
import sys
import pdb
import math
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits import axisartist

def get_cdf(x):
    n = len(x)
    y = np.array(range(n))/float(n)
    return x.sort_values(), y

def get_cdf_2(x):
    n = len(x)
    ys = range(100)
    xsorted = sorted(x)
    xs = [xsorted[int((y * n) / 100)] for y in range(99)] + [xsorted[-1]]
    return xs, ys

def plot_scatter(x, y, xlabel='[Add xlabel]', ylabel='[Add ylabel]', title='[Add title]', filename='new_plot'):
    plt.scatter(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(f'./plots/{filename}')

def plot_cdf(x, xlabel='[Add xlabel]', title=f'CDF', filename='new_cdf'):
    x_ax, y_ax = get_cdf(x)
    plt.xlabel(xlabel)
    plt.ylabel('Pr')
    plt.title(title)
    plt.plot(x_ax, y_ax, marker='o')
    plt.savefig(f'./plots/{filename}')

#qlen vs heap_util_pct; heap_util_pct vs YGCT; YGCT vs latency; latency vs qlen
def plot_all(ts, qlen, heap_util, YGCT, FGCT, latency):
    fig, axs = plt.subplots(5, 2, figsize=(8,8))
    fig.tight_layout()
    axs[0, 0].scatter(qlen, heap_util)
    axs[0, 0].set_title('qlen vs heap_util_pct')
    axs[0, 1].scatter(heap_util, YGCT)
    axs[0, 1].set_title('heap_util_pct vs YGCT_ms')
    axs[1, 0].scatter(YGCT, latency)
    axs[1, 0].set_title('YGCT_ms vs latency_ms')
    axs[1, 1].scatter(latency, qlen)
    axs[1, 1].set_title('latency_ms vs qlen')
    axs[2, 0].plot(ts, qlen)
    axs[2, 0].set_title('qlen_TimeSeries')
    axs[2, 1].plot(ts, heap_util)
    axs[2, 1].set_title('heap_util_TimeSeries')
    axs[3, 0].plot(ts, YGCT)
    axs[3, 0].set_title('YGCT_TimeSeries')
    axs[3, 1].plot(ts, latency)
    axs[3, 1].set_title('latency_TimeSeries')
    axs[4, 0].plot(ts, FGCT)
    axs[4, 0].set_title('FGCT_TimeSeries')
    axs[4, 1].scatter(FGCT, latency)
    axs[4, 1].set_title('FGCT_ms vs latency_ms')
    
    plt.savefig(f'./measurement_plots.png')

def plot_all_2(df: pd.DataFrame):
    fig, axs = plt.subplots(4, 3, figsize=(8,8))
    fig.tight_layout()
    axs[0, 0].plot(df['timestamp'], df['qlen'])
    axs[0, 0].set_title('qlen Timeseries')
    axs[1, 0].plot(df['timestamp'], df['YGCT'])
    axs[1, 0].set_title('YGCT Timeseries')
    axs[2, 0].plot(df['timestamp'], df['FGCT'])
    axs[2, 0].set_title('FGCT Timeseries')
    axs[3, 0].plot(df['timestamp'], df['latency_ms'])
    axs[3, 0].set_title('Latency Timeseries')
    axs[0, 1].scatter(df['qlen'], df['YGCT'])
    axs[0, 1].set_title('qlen vs YGCT')
    axs[1, 1].scatter(df['YGCT'], df['latency_ms'])
    axs[1, 1].set_title('YGCT vs latency')
    axs[2, 1].scatter(df['latency_ms'], df['qlen'])
    axs[2, 1].set_title('latency vs qlen')
    axs[3, 1].plot(df['timestamp'], df['S0'])
    axs[3, 1].set_title('S0_util Timeseries')
    axs[0, 2].plot(df['timestamp'], df['S1'])
    axs[0, 2].set_title('S1_util Timeseries')
    axs[1, 2].plot(df['timestamp'], df['E'])
    axs[1, 2].set_title('Eden_util Timeseries')
    axs[2, 2].plot(df['timestamp'], df['O'])
    axs[2, 2].set_title('Oldspace_util Timeseries')
    axs[3, 2].plot(df['timestamp'], df['M'])
    axs[3, 2].set_title('Metaspace_util Timeseries')

    plt.savefig(f'./measurement_plots.png')

def plot_all_3(df: pd.DataFrame):
    fig, axs = plt.subplots(4, 1, figsize=(8,8))
    fig.tight_layout()
    axs[0].plot(df['timestamp'], df['qlen'])
    axs[0].set_title('qlen Timeseries')
    axs[1].plot(df['timestamp'], df['GCT'])
    axs[1].set_title('GCT Timeseries')
    axs[2].plot(df['timestamp'], df['rps'])
    axs[2].set_title('RPS Timeseries')
    axs[3].plot(df['timestamp'], df['latency_ms'])
    axs[3].set_title('Latency Timeseries')
    
    plt.savefig(f'./measurement_plots.png')

def plot_all_in_one(df: pd.DataFrame):
    FS=16
    fig = plt.gcf()
    fig.set_size_inches(10, 3.5)
    plt.style.use('seaborn-colorblind')
    
    host = host_subplot(111, axes_class=axisartist.Axes)
    plt.subplots_adjust(right=0.75)
    par1 = host.twinx()
    par2 = host.twinx()

    par2.axis['right'] = par2.new_fixed_axis(loc='right', offset=(55, 0))

    par1.axis['right'].toggle(all=True)
    par2.axis['right'].toggle(all=True)
    
    p1, = host.plot(df['timestamp'], df['rps'], label='Requests per second')
    p2, = par1.plot(df['timestamp'], df['GCT'], label='GC duration (ms)')
    p3, = par2.plot(df['timestamp'], df['qlen'], label='Queue length')

    host.set_xlabel('Time (s)')
    host.set_ylabel('Requests per second')
    par1.set_ylabel('GC duration (ms)')
    par2.set_ylabel('Queue length')

    host.set_xlim(left=0, right=1200) 
    par1.set_xlim(left=0, right=1200) 
    par2.set_xlim(left=0, right=1200) 
    #host.legend()

    host.axis['bottom'].label.set_fontsize(FS)
    host.axis['left'].label.set_fontsize(FS)
    par1.axis['right'].label.set_fontsize(FS)
    par2.axis['right'].label.set_fontsize(FS)

    host.axis['left'].label.set_color(p1.get_color())
    par1.axis['right'].label.set_color(p2.get_color())
    par2.axis['right'].label.set_color(p3.get_color())
    plt.savefig(f'./measurement_plots.png', bbox_inches='tight')
    
def main():
    measurements_path = ''
    if len(sys.argv) == 2:
        #print(f"Please give a job table and a GC table:")
        #sys.exit(0)
        measurements_path = sys.argv[1]
    else:
        measurements_path = 'measurement.csv'

    df = pd.read_csv(f'./{measurements_path}')
    df = df[df['timestamp']>30] #ignore warming up part                                                                                                                                       

    df = df.groupby(df['timestamp']//48).mean() #originally 48
    base = df['timestamp'].iloc[0]
    df['timestamp'] = df['timestamp'] - base
    plot_all_in_one(df)
    #plot_all_3(df)

if __name__=="__main__":
    main()
