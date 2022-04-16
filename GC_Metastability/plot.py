#!/usr/bin/python3
import pandas as pd
import sys
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits import axisartist

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
        measurements_path = sys.argv[1]
    else:
        measurements_path = 'measurement.csv' # default input file

    df = pd.read_csv(f'./{measurements_path}')
    df = df[df['timestamp']>30] #ignore warming up part                                                                                                                                       
    df = df.groupby(df['timestamp']//48).mean()
    base = df['timestamp'].iloc[0]
    df['timestamp'] = df['timestamp'] - base
    plot_all_in_one(df)

if __name__=="__main__":
    main()
