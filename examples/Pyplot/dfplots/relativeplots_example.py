#!/usr/bin/python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other packages
import numpy as np
import matplotlib.pyplot as plt
import math

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.yoko750 as yk

fileName = "/home/jaime/Documents/My Papers/Dropped/Recoil " \
           "Streamers/Data/081713/Scope25/D0001"

f = yk.Yoko750File(fileName)
header = f.get_header()

wantOffset = 'y'

traces = {'E-16Hi':9, 'II_VL':15}	# Specifies which traces you want to look at
traceUnits = {'E-16Hi':'V/m', 'II_VL':'A'} # Specifies the units for each trace for plotting
traceUnitsFactors = {'E-16Hi':1, 'II_VL':1} # Specifies the unit conversion factor 
									# for plotting

calFactors = {'E-16Hi':8251.86, 'II_VL':205.946} # Specifies the calibration factor for each
								# trace
df32_tStart = {'E-16Hi':0, 'II_VL':0} # Gives the starting time of interest for
									# each trace
df32_tStop = {'E-16Hi':2, 'II_VL':2}	# Gives the ending time of interes for
								# each trace
								
traceKeys = traces.keys()	# Gets the key names for each trace to be used 
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
#~ fig = plt.figure()
#~ 
#~ ax1 = fig.add_subplot(211)
#~ ax1.plot(results['II_VL'].dataTime, \
#~          results['II_VL'].data*traceUnitsFactors['II_VL'])
#~ ax1.set_title('II_VL')
#~ ax1.set_ylabel('Current (%s)' % traceUnits['II_VL'])
#~ 
#~ ax2 = fig.add_subplot(212)
#~ ax2.plot(results['E-16Hi'].dataTime, \
#~          results['E-16Hi'].data*traceUnitsFactors['E-16Hi'])
#~ ax2.set_title('E-16Hi')
#~ ax2.set_xlabel('Time (seconds)')
#~ ax2.set_ylabel('Current (%s)' % traceUnits['E-16Hi'])
#~ 	
#~ p = [df.plotdf(fig,ax1), df.plotdf(fig, ax2)]

#~ fig = plt.figure()
#~ ax1 = fig.add_subplot(111)
#~ ax1.plot(results['II_VL'].dataTime, \
#~          results['II_VL'].data*traceUnitsFactors['II_VL'])
#~ ax1.set_title('II_VL')
#~ ax1.set_ylabel('Current (%s)' % traceUnits['II_VL'])
#~ ax1.set_xlabel('Time (seconds)')
#~ 
#~ p1 = df.plotdf(fig, ax1, max_points=1E4)
#~ p1.plot()

rt1 = df.RelativeTimePlot(results['II_VL'].dataTime, results['II_VL'].data*traceUnitsFactors['II_VL'])
rt1.plot()

rt2 = df.RelativeTimePlot(results['E-16Hi'].dataTime, results['E-16Hi'].data*traceUnitsFactors['E-16Hi'], draw=False)

#~ fig = plt.figure()
#~ ax2 = fig.add_subplot(111)
#~ ax2.plot(results['E-16Hi'].dataTime, \
#~          results['E-16Hi'].data*traceUnitsFactors['E-16Hi'])
#~ ax2.set_title('E-16Hi')
#~ ax2.set_xlabel('Time (seconds)')
#~ ax2.set_ylabel('Current (%s)' % traceUnits['E-16Hi'])
#~ 
#~ p2 = df.plotdf(fig, ax2)
#~ p2.plot()

#~ s = df.syncdf(p)
#~ s.plot_all()
plt.show()

axes = []

fig, ax = rt1.relative_plot(1E3)
ax.set_xlabel('Time (milliseconds)')

ax.set_title('II_VL')
ax.set_ylabel(traceUnits['II_VL'])
ax.grid()

axes.append(ax)

rt2.x_bounds = rt1.x_bounds
rt2.zero_time = rt1.zero_time
rt2.delta_t = rt1.delta_t

fig, ax = rt2.relative_plot(1E3)
ax.set_xlabel('Time (milliseconds)')

ax.set_title('E-16Hi')
ax.set_ylabel(traceUnits['E-16Hi'])
ax.grid()

axes.append(ax)

t = axes[0].get_lines()[0].get_xdata()

y1 = axes[0].get_lines()[0].get_ydata()
y2 = axes[1].get_lines()[0].get_ydata()
    
plt.figure()
plt.subplot(211)
plt.plot(t, y1)
plt.ylabel(axes[0].get_ylabel())
plt.title(axes[0].get_title())
plt.xlim(axes[0].get_xlim())
plt.grid()

plt.subplot(212)
plt.plot(t, y2)
plt.title(axes[1].get_title())
plt.ylabel(axes[1].get_ylabel())
plt.xlabel(axes[1].get_xlabel())
plt.xlim(axes[1].get_xlim())
plt.grid()

plt.show()
