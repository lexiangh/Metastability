import matplotlib.pyplot as plt
import math 
import numpy as np
from scipy.stats import zipf 
import random
from scipy.stats import zipfian 
import json
# exponential function x = 10^y
datax = []
#plt.style.reload_library()
plt.style.use('ieee')
alpha = 1.00001
max_entries_in_db = 34511000
datay1 = []
datay3 = []
timeout1 = 0
timeout2 = 0

with open('timeout_vulnerability_region_config.json') as json_file:
    data = json.load(json_file) 
    alpha = float(data["alpha"]) 
    datax = data["load"]
    datay1 = data["triggers_for_timeout1"]
    datay3 = data["triggers_for_timeout2"]
    timeout1 = data["timeout1"]
    timeout2 = data["timeout2"]

"""
datay1 = [ math.inf, math.inf , 1000000, 100000, 10000, 3126] 
datay3 = [ math.inf, math.inf , 100000000, 10000000, 1000000, 312600]
"""
datay1_t = [math.inf, math.inf] 
datay3_t = [math.inf, math.inf]
max_y = [1, 1]

for i in range(2, len(datay1)):
    datay1_t.append(zipfian.cdf(datay1[i], alpha,max_entries_in_db)) 
    datay3_t.append(zipfian.cdf(datay3[i], alpha,max_entries_in_db))
    max_y.append(1)
    
yticks = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000] 

cache_hit_rates = []
for i in yticks:
    cache_hit_rates.append(zipfian.cdf(i, alpha,max_entries_in_db))

ax = plt.gca()
ax.set_xlim([60, 360])
ax.set_ylim([0,1])
ax.axvspan(60, 180, color='skyblue')

plt.ylabel("Drop in cache hit rate")
plt.xlabel("Requests per second")

plt.plot(datax,datay1_t,   color = 'purple', linewidth = 1.5) 
plt.plot(datax,datay3_t,   color = 'black', linewidth =1.5)

#plt.fill_between(datax, datay1_t,datay3_t, color='red', alpha= 0.5)
plt.fill_between(datax, datay1_t, max_y, color='red')
plt.fill_between(datax, datay3_t, color='orange')
plt.fill_between(datax, datay1_t , datay3_t, color='red',hatch=r"//", edgecolor="orange")

plt.rcParams["hatch.linewidth"] = 4
plt.xticks(datax)
#plt.yticks(cache_hit_rates)

t0 = plt.text(240, .60, f"{timeout1} sec timeout", color = "white", rotation = -15, weight = 'bold' ) 
t0.set_bbox(dict(facecolor='purple', alpha=0.6, edgecolor='purple'))
t1 = plt.text(235, .40, f"{timeout2} sec timeout",  color = "white", rotation = -15, weight = 'bold' )
t1.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='black'))

plt.text(88, 0.87, "Stable region", color='black', weight = 'bold')
plt.text(195, 0.87, "Metastable failure region", color='black', weight = 'bold')
plt.text(88, 0.1, "No metastablity\n for any \ntrigger size", color='black', rotation=90, weight = 'bold') 
plt.text(230, 0.225, "Vulnerable region", color='black', weight = 'bold')

figure = plt.gcf()
figure.set_size_inches(4, 2)
plt.savefig("Vulnerability region_Cache_With_Varying_Timeouts.png", dpi = 400)