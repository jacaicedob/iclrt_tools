#!/usr/bin/env python

import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import sys

import xml.etree.ElementTree as ET

color_cycle = ['#FAA43A', '#5DA5DA', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854', '#4D4D4D']

c = 3.0E8

if len(sys.argv) < 2:
    print("Not enough parameters.")
    sys.exit(1)


eventName = sys.argv[1]

if "uf" in eventName.lower():
    xml_file = '../../Data Sets/XML/%s.xml' % eventName
else:
    xml_file = '../../Data Sets/XML/UF%s.xml' % eventName
    
root = ET.parse(xml_file)

eventName = root.find('name').text
eventNamef = "%s%s%s" % (eventName[0:2], eventName[3:5], eventName[6:])

mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Current Reflections/LaTex/Pictures/'

for rss in root.iter('return_stroke'):
    eventRS = int(rss.find('number').text)
    
    fileName = './DataFiles/%s_I_RS%d.p' % (eventNamef, eventRS)

    data = pickle.load(open(fileName, 'rb'))
        
    i_fit = data['i_model']
    time = data['time'] - 5E-6
    i_r = data['i_r']
    ii_hi = data['ii_hi']
    tau = data['tau']
    di = data['di']
    di_factor = data['di_factor']

    """
    Plots for individual files
    """
    mpl.rcParams['axes.color_cycle'] = color_cycle
    sup_title = '%s %s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

    #~ xlabel = r'Time (microseconds)'
    xlabel = 'Time ($\mu$s)'
    xfactor = 1E6

    ylabel = 'Current (kA)'
    yfactor = 1E-3

    xlim = [-1,25]
    ylim = [-10, 30]


    fig = plt.figure()#figsize=(1024/150, 768/150))
    #fig.suptitle(sup_title, fontsize=20)
    
    ax = fig.add_subplot(111)
    ax.plot(time*xfactor, i_fit*yfactor, '--', linewidth=3.0,
            label=r'Fitted ($\propto e^{-t/\tau}$)', c='#FAA43A')
    ax.plot(time*xfactor, ii_hi*yfactor, linewidth=3.0, label=r'Measured', c='#5DA5DA')
    ax.plot(time*xfactor, -1.0*i_r*yfactor, '--', linewidth=3.0,
            label=r'Reflected', c='#60BD68')
    ax.set_title(sup_title)
    #~ ax.set_xlabel(xlabel)
    #~ ax.set_ylabel('(kA)')#ylabel)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(True,which='both')
    #ax.autoscale(enable=True, axis='both', tight=True)

    handles, labels = ax.get_legend_handles_labels()
    handles[0], handles[1] = handles[1], handles[0]
    labels[0], labels[1] = labels[1], labels[0]
    ax.legend(handles, labels, prop={'size':20})
    # plt.legend(prop={'size':20})

    #~ fig, (ax1, ax2, ax3) = plt.subplots(3,1,sharex=True)#, figsize=(1024/150, 768/150))
    #~ fig.suptitle(sup_title)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(time*xfactor, ii_hi*yfactor, linewidth=3.0)
    ax1.set_title('Measured')
    #~ ax1.set_ylabel('(kA)')#ylabel)
    ax1.set_xlim(xlim)
    #~ ax1.set_ylim(ylim)
    ax1.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax1.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.grid(True,which='both')

    fig = plt.figure()
    ax2 = fig.add_subplot(111)
    ax2.plot(time*xfactor, i_fit*yfactor, linewidth=3.0)
    ax2.set_title('Fitted')
    #~ ax2.set_ylabel('(kA)')#ylabel)
    ax2.set_xlim(xlim)
    #~ ax2.set_ylim(ylim)
    ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax2.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.grid(True,which='both')

    fig = plt.figure()
    ax3 = fig.add_subplot(111)
    ax3.plot(time*xfactor, -i_r*yfactor, linewidth=3.0)
    ax3.set_title('Reflection')
    #~ ax3.set_xlabel(xlabel)
    #~ ax3.set_ylabel('(kA)')#ylabel)
    ax3.set_xlim(xlim)
    #~ ax3.set_ylim(ylim)
    ax3.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax3.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.grid(True,which='both')

    plt.show()
