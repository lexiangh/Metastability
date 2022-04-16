import matplotlib.pyplot as plt
import math 
import numpy as np
from scipy.stats import zipf 
import random
from scipy.stats import zipfian 
import json

# exponential function x = 10^y
datax = [  ] # loads 
#plt.style.reload_library()
plt.style.use('ieee')

max_entries_in_db = 34511000
alpha2 = 1.00001
alpha1 = 1.14165
# triggers for 95% CHR
datay1 = [ ]  
# triggers for 80% CHR 
datay3 = [ ] 

with open('hitrate_vulnerability_region_config.json') as json_file:
    data = json.load(json_file) 
    alpha2 = float(data["alpha2"])
    alpha1 = float(data["alpha1"])
    datax = data["load"]
    datay1 = data["triggers_for_alpha1"]
    datay3 = data["triggers_for_alpha2"]

len1 = len(datay1)
for i in range(0, len1):
    if(datay1[i] == -1):
        datay1[i] = math.inf
    if(datay3[i] == -1):
        datay3[i] = math.inf



# color blind color palette 
opacity = 0.5
colors = {
    'blue':   [55,  126, 184],  #377eb8 
    'orange': [255, 127, 0],    #ff7f00
    'green':  [77,  175, 74],   #4daf4a
    'pink':   [247, 129, 191],  #f781bf
    'brown':  [166, 86,  40],   #a65628
    'purple': [152, 78,  163],  #984ea3
    'gray':   [153, 153, 153],  #999999
    'red':    [228, 26,  28],   #e41a1c
    'yellow': [222, 222, 0]     #dede00
}  
c_str = {k:f'rgba({v[0]},{v[1]},{v[2]},{opacity})'
         for (k, v) in colors.items()}
c_str['yellow']  # Gives the rgba string for 'yellow'




def get_chr(trigger_size, alpha_):
    return zipfian.cdf(trigger_size, alpha_, max_entries_in_db)

"""
datay1 = [ math.inf, math.inf , 1000000, 100000, 10000, 3126]
datay2 = [ math.inf, math.inf , 10000000, 1000000, 100000, 1000]
datay3 = [ math.inf, math.inf , 100000000, 10000000, 1000000, 312600]
"""
datay1_t = [math.inf, math.inf, math.inf] 
datay3_t = [math.inf, math.inf, get_chr(316227, alpha2)]
max_y = [1, 1, 1]

for i in range(3, len(datay1)):
    datay3_t.append(zipfian.cdf(datay3[i], alpha2,max_entries_in_db))
    max_y.append(1)
    

for i in range(3, len(datay1)):
    datay1_t.append(zipfian.cdf(datay1[i], alpha1,max_entries_in_db)) 
    
yticks = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000] 

cache_hit_rates = []
for i in yticks:
    cache_hit_rates.append(zipfian.cdf(i, alpha2,max_entries_in_db))

ax = plt.gca()
ax.set_xlim([60, 1200])
ax.set_ylim([0,1])
ax.axvspan(60, 180, color='skyblue')
#ax.axvspan(180, 240, alpha=0.5, color='skyblue')

plt.ylabel("Drop in cache hit rate")
plt.xlabel("Requests per second")

plt.plot(datax,datay1_t, color = 'purple', linewidth = 1.5)
#plt.plot(datax,datay2_t,    color = 'crimson', linewidth = 2)
plt.plot(datax,datay3_t, color = 'black', linewidth =1.5)

plt.fill_between(datax, datay1_t,datay3_t, color='orange',hatch=r"//", edgecolor="red")
plt.fill_between(datax, datay1_t, max_y, color='red')
plt.fill_between(datax, datay3_t, color='orange')


mini_green_area_x = [180, 240]
mini_green_area_y = [get_chr(316227, alpha1), get_chr(31622, alpha1)]
mini_green_area_max_y = [1,1] 
plt.fill_between(mini_green_area_x, mini_green_area_y, mini_green_area_max_y,hatch=r"//", color = "skyblue", edgecolor="red")
plt.fill_between(mini_green_area_x, mini_green_area_y,hatch=r"//", color = "skyblue", edgecolor="orange")

plt.rcParams["hatch.linewidth"] = 4


#plt.fill_between(x, a3, a4, color='green',alpha=0.5,hatch=r"//")

#plt.xticks(datax)
#plt.yticks(cache_hit_rates) 
t0 = plt.text(500, .725, "~95% Hit rate", rotation = -5 ,color = "white" , weight='bold') 
t0.set_bbox(dict(facecolor='purple', alpha=0.6, edgecolor='purple'))

t1= plt.text(250, .09, "~80% Hit rate", weight='bold', rotation = -55 , color = "white")  
t1.set_bbox(dict(facecolor='black', alpha=0.6, edgecolor='black'))

plt.text(100, 0.25, "Stable region", weight='bold', color='black', rotation = 90)
#plt.text(88, 0.1, "no metastablity\n for any trigger", color='black', rotation=90) 
t2 = plt.text(600, 0.2, "Vulnerable region", weight='bold', color='black')
plt.text(600, 0.9, "Metastable failure region", color='black',weight='bold')
t2.set_bbox(dict(facecolor='orange', ec='orange'))

figure = plt.gcf()
figure.set_size_inches(4, 2)
plt.savefig("Vulnerability region_Cache_With_Varying_HitRates.png", dpi = 400)

 