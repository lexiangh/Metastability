import matplotlib.pyplot as plt
import math 
import numpy as np
from scipy.stats import zipf 
import random

# exponential function x = 10^y
datax = [ 60, 120, 180, 240, 300, 360 ]
datay = [ math.inf, math.inf , 1000000, 100000, 10000, 3126]

max_datax = [60, 120, 180]
max_datay = [10000000,10000000,10000000]
yticks = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000] 

ax = plt.gca()
ax.set_xlim([60, 360])

plt.fill_between(datax, datay, color='orange')
plt.fill_between(datax, datay,  10000000, color='red')
plt.fill_between(max_datax, max_datay, color='lime')
#convert x-axis to Logarithmic scale
plt.yscale("log")
plt.ylabel("trigger size")
plt.xlabel("arrival rate")
plt.plot(datax,datay, "--", color = 'red')
plt.xticks(datax)
plt.yticks(yticks)
plt.text(88, 500000.5, "stable region", color='black', fontsize=14)
plt.text(88, 45.5, "no metastable issue\n for any trigger size", color='black', fontsize=14, rotation=90)
plt.text(240, 45.5, "vulnerable region", color='black', fontsize=14)
plt.text(240, 500000.5, "metastable region", color='black', fontsize=14)
plt.title("Critical trigger sizes to cause metastable failures at vulnerable states")
plt.savefig("test.png")