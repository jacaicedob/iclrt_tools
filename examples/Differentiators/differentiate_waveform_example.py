#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import JaimePackages.plotting.dfplots as df
import JaimePackages.oscilloscopes.lecroy as lc
import JaimePackages.oscilloscopes.yoko750 as yk750
import JaimePackages.oscilloscopes.yoko850 as yk850
import JaimePackages.differentiators.differentiate_waveform as diff

dataFile = "/home/jaime/Documents/My Papers/Ongoing/Current Reflections/" \
           "Raw Data/081713/Scope18/C4AC00001.trc"

f = lc.lecroy_data(dataFile)

wantOffset = False
trace = 1
traceUnit = 'V/m'
traceUnitsFactor = 1.0

calFactor = 1
df32_tStart = 9.99993682e-001
df32_tStop = 1.00003088e+000

f.get_seg_time()
f.get_segment(trace, calFactor)

t, d_dt, wave = diff.differentiate(f.dataTime-df32_tStart, f.data)
d_dt *= 1E9

fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(t*1E6, wave)
ax2.plot(t*1E6, d_dt)

ax1.set_ylabel('E (V/m)')
ax2.set_ylabel('dE/dt (kV/m/$\mu$s)')

ax2.set_xlabel('Time ($\mu$s)')

plt.show()
