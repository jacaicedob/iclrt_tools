#!/usr/bin/env python

# Add personal packages directory to path
import sys
import iclrt_tools.differentiators.differentiate_waveform as diff
import iclrt_tools.plotting.dfplots as df
import iclrt_tools.filters.filters as filters
import pickle
import matplotlib.pyplot as plt
import os
import numpy as np

parent = '/home/jaime/Documents/Python Code/Data Sets/DataFiles/'

files = None

for root, dir, file in os.walk(parent):
    if root == parent:
        files = file

for file in files:
    print(file)
    data = pickle.load(open(parent+file, 'rb'))['II_HI']
    t = data.dataTime * 1E-6
    i = data.data

    __, di, __ = diff.differentiate(t, i)

    i = i / np.max(i)
    di = di / np.max(di)

    di_filtered = filters.moving_average(di)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(t, i, t, di_filtered)
    ax.set_title(file[0:6] + '_'+ file[-8:-5] + ' - Normalized and filtered dI/dt (5 pt MA)')
    p = df.pickerPlot(fig, ax)
    p.plot()

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(t, i, t, di)
    ax1.set_title(file[0:6] + '_'+ file[-8:-5] + '- Normalized raw data')
    p1 = df.pickerPlot(fig1, ax1)
    p1.plot()
    plt.show()
