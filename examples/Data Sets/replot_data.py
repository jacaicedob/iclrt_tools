#!/usr/bin/env python

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import cm

import sys
import pickle
import operator

eventDate = '061809'
eventName = '0920'
rs = 3

fileSave = "./DataFiles/UF%s_data_%s_rs%d.p" % (eventName, eventDate, rs)

# Read in file and plot data

data = pickle.load(open(fileSave, "rb"))
    
event = 'UF %s-%s RS%d' % (eventName[:2], eventName[2:], rs)

keys = data.keys()
data_only = {}
ignore = ['time', 'axes', 'dE_8', 'dE_3', 'dE_1', 'dE_7', 'dE_4']

for i,key in enumerate(keys):
    if key in ignore:
        pass
    else:
        data_only[key] = data[key]

keys = data_only.keys()
sort_data = {}

for i,key in enumerate(keys):
    value = data['axes'][key].get_title().split()
    
    if len(value) == 4:
        s = value[3]
        ind = s.find('km')
        
        if ind > 0:
            temp = int(value[3][:ind])
            s = '%d' % (temp*1E3)
        
        ind = s.find('m')
        
        if ind > 0:
            s = value[3][:ind]
        
        sort_data[key] = int(s)
        
    else:
        s = value[4]
        ind = s.find('km')
        
        if ind > 0:
            temp = int(value[4][:ind])
            s = '%d' % (temp*1E3)
        
        ind = s.find('m')
        
        if ind > 0:
            s = value[4][:ind]
        
        sort_data[key] = int(s)
    
sorted_data = sorted(sort_data.items(), key=operator.itemgetter(1))

l = len(sorted_data)-1

zoom_lim = [0, 20]

fig, ax2 = plt.subplots(1,1)
fig.suptitle(event, fontweight='bold')

temp_data = data[sorted_data[1][0]][::int(len(data[sorted_data[1][0]])/len(data['time']))]

if 'dE' in sorted_data[1][0]:
    title = 'Integrated %s (D = %d m)' % (sorted_data[1][0], sorted_data[1][1])
else:
    title = '%s (D = %d m)' % (sorted_data[1][0], sorted_data[1][1])

ax2.plot(data['time'], temp_data*1E-3)
ax2.set_title('%s' % title)
ax2.set_xlim(zoom_lim)
ax2.set_ylabel('kV/m')
ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax2.grid(True,which='both')
ax2.set_xlabel('Time ($\mu$s)')


fig, (ax1,ax2) = plt.subplots(2, 1, sharex=True)
fig.suptitle(event, fontweight='bold')

temp_data = data[sorted_data[1][0]][::int(len(data[sorted_data[1][0]])/len(data['time']))]

ax1.plot(data['time'],data[sorted_data[0][0]]*1E-3)        
ax1.set_title('II_HI')
ax1.set_xlim(zoom_lim)
ax1.set_ylabel('kA')
ax1.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax1.grid(True,which='both')

if 'dE' in sorted_data[1][0]:
    title = 'Integrated %s (D = %d m)' % (sorted_data[1][0], sorted_data[1][1])
else:
    title = '%s (D = %d m)' % (sorted_data[1][0], sorted_data[1][1])

ax2.plot(data['time'], temp_data*1E-3)
ax2.set_title('%s' % title)
ax2.set_xlim(zoom_lim)
ax2.set_ylabel('kV/m')
ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax2.grid(True,which='both')
ax2.set_xlabel('Time ($\mu$s)')


for i in range(int((l-1)/2)):
    #~ zoom_lim = [0, 30]
    fig, (ax1,ax2, ax3) = plt.subplots(3, 1, sharex=True)
    fig.suptitle(event, fontweight='bold')

    temp_data = data[sorted_data[2*i+2][0]][::int(len(data[sorted_data[2*i+2][0]])/len(data['time']))]
    
    ax1.plot(data['time'],data[sorted_data[0][0]]*1E-3)        
    ax1.set_title('II_HI')
    ax1.set_xlim(zoom_lim)
    ax1.set_ylabel('kA')
    ax1.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.grid(True,which='both')
    
    if 'dE' in sorted_data[2*i+2][0]:
        title = 'Integrated %s (D = %d m)' % (sorted_data[2*i+2][0], sorted_data[2*i+2][1])
    else:
        title = '%s (D = %d m)' % (sorted_data[2*i+2][0], sorted_data[2*i+2][1])
    
    ax2.plot(data['time'], temp_data*1E-3)
    ax2.set_title('%s' % title)
    ax2.set_xlim(zoom_lim)
    ax2.set_ylabel('kV/m')
    ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.grid(True,which='both')
    
    if 'dE' in sorted_data[2*i+3][0]:
        title = 'Integrated %s (D = %d m)' % (sorted_data[2*i+3][0], sorted_data[2*i+3][1])
    else:
        title = '%s (D = %d m)' % (sorted_data[2*i+3][0], sorted_data[2*i+3][1])
    
    ax3.plot(data['time'], temp_data*1E-3)
    ax3.set_title('%s' % title)
    ax3.set_xlim(zoom_lim)
    ax3.set_ylabel('kV/m')
    ax3.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.grid(True,which='both')
    ax3.set_xlabel('Time ($\mu$s)')


plt.show()
