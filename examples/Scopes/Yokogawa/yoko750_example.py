#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
import matplotlib.pyplot as plt
import math

import iclrt_tools.oscilloscopes.yoko750 as yk


#~ fileName = "/Volumes/OSX2/Users/jaime/My Papers/Current Reflections/UF 09-20 061809/Waveforms/Scope24/D0001"
           
fileName = "/home/jaime/Documents/My Papers/Ongoing/Current Reflections/" \
           "UF 13-09 060913/Waveforms/Scope25/D0001"
           
f = yk.Yoko750File(fileName)
header = f.get_header()

wantOffset = 'y'

traces = {'II_HI':13, 'II_LO':14, 'II_VL':15}   # Specifies which traces you want to look at
traceUnits = {'II_HI':'kA', 'II_LO':'A', 'II_VL':'A'} # Specifies the units for each trace for plotting
traceUnitsFactors = {'II_HI':1E-3, 'II_LO':1, 'II_VL':1}    # Specifies the unit conversion factor 
                                    # for plotting

calFactors = {'II_HI':20202.02, 'II_LO':1956.95, 'II_VL':78.59} # Specifies the calibration factor for each
                                # trace
df32_tStart = {'II_HI':0, 'II_LO':0, 'II_VL':0} # Gives the starting time of interest for
                                    # each trace
df32_tStop = {'II_HI':2, 'II_LO':2, 'II_VL':2}  # Gives the ending time of interes for
                                # each trace
                                
traceKeys = traces.keys()   # Gets the key names for each trace to be used 
                            # as an index for the other dictionaries

results = {}
for key in traceKeys:
    print("Obtaining trace: '%s'" % key)
    results[key] = f.get_trace_data(header, traces[key], df32_tStart[key], \
                                    df32_tStop[key], calFactors[key], \
                                    wantOffset)
                                    
for key in traceKeys:
    print("%s ID: %s" % (key,results[key].traceLabel))

#~ print results['II_HI'].dataTime.shape[0]
#~ print results['II_HI'].data.shape[0]

print("Plotting results...")
for key in traceKeys:
    plt.figure()
    plt.plot(results[key].dataTime*1E6, \
             results[key].data*traceUnitsFactors[key])
    plt.title(key)
    plt.xlabel('Time ($\mu$seconds)')
    plt.ylabel('Current (%s)' % traceUnits[key])
    plt.show()

