#!/usr/bin/env python

import sys
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/dfplots/')

import dfplots as df
import lma_tools
import matplotlib.pyplot as plt
import numpy as np

"""
Get data from file
"""

file_name = "/home/jaime/Documents/LMA/Data/Triggered/ByDate/061114/UF14-07/LYLOUT_140611_183421_0008.dat"

date, center, lma_sources = lma_tools.read_lma(file_name)

num_stations = 5
max_chi_squared = 5
max_alt = 20E3  # meters

"""
Run filters on data (adapted from Brian Hare's plot_lma.py code)
"""
# Chi-squared no greater than max_chi_squared
sources = lma_tools.chi_filter(lma_sources,max_chi_squared)

# Force LMA sources to calculate number of stations
sources = lma_tools.calc_stations(sources)

# Filter so each source must have 'num_stations' or more stations
sources = lma_tools.station_filter(sources,num_stations)

# Filter so each source is below max_alt
sources = lma_tools.alt_filter(sources, max_alt)

# Replace list with filtered sources
sources = list(sources)


"""
Plot the sources
"""
   
fig, ax, hist = lma_tools.lma_plotter(date, center, sources).plot()
ax.set_ylim(0,max_alt*1E-3)
ax.set_title('LMA Data')
ax.set_ylabel('Altitude (km)')
ax.set_xlabel('Time')

hist.set_title('Altitude Histogram')
hist.set_ylabel('Altitude')
hist.set_xlabel('Number of sources')
hist.set_ylim(0,max_alt*1E-3)

plt.show()
