#!/usr/bin/env python

# Add personal packages directory to path
import sys

# Import other packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import operator
import pickle
import xml.etree.ElementTree as ET

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.yoko850 as yk
import iclrt_tools.models.current_fit.current_fit as cf


### Setup file information and read the file
eventName = '1308'
xml_file = '../../Data Sets/XML/UF%s.xml' % eventName
#~ tau = 18.0E-6

root = ET.parse(xml_file)

day = root.find('date').find('day').text
month = root.find('date').find('month').text
year = root.find('date').find('year').text[-2:]

eventDate = '%s%s%s' % (month, day, year)
eventName = root.find('name').text
eventNamef = "%s%s%s" % (eventName[0:2], eventName[3:5], eventName[6:])

for rss in root.iter('return_stroke'):
    rs = int(rss.find('number').text)

    fileSave = "../../Data Sets/DataFiles/%s_data_%s_rs%d.p" % (eventNamef, eventDate, rs)
    data = pickle.load(open(fileSave, "rb"))

    ii_hi = []

    for key in data.keys():
        if key.lower() == 'ii_hi_24' and not(any(ii_hi)):
            ii_hi = data[key]['data']
            time = data[key]['time'] + abs(data[key]['time'][0])

        elif key.lower() == 'ii_hi' and not(any(ii_hi)):
            ii_hi = data[key]['data']
            time = data[key]['time'] + abs(data[key]['time'][0])

    """
    One time
    """
    data = {}

    data['i_model'] = ii_hi
    data['time'] = time
    data['i_r'] = 0
    data['ii_hi'] = ii_hi
    data['tau'] = 0
    #~ data['di'] = di
    #~ data['di_factor'] = di_factor
    data['ind'] = 0

    fileSave = './DataFiles/%s_I_RS%d.p' % (eventNamef, rs)
    pickle.dump(data, open(fileSave, "wb"))

    plt.plot(time, ii_hi)
    plt.show()

    sys.exit(0)


    """
    For TL modeling
    """
    time *= 1E-6

    tau = input("Enter tau value (in us) for RS %s:  " % rs)
    tau = int(tau)
    tau *= 1E-6

    #~ window_length = 1.0
    #~ weights = np.repeat(1.0, window_length)/window_length
    #~ y_filtered = np.convolve(ii_hi, weights, 'same')
    #~ ii_hi = y_filtered

    cft = cf.CurrentFitTail(time, ii_hi, tau)
    cft.fit()
    delta_t = np.diff(time)[0]

    #~ i = ii_hi[int(cft.p.x_bounds[0]/delta_t):int((cft.p.x_bounds[-1] + 100E-6)/delta_t)]
    sig_len = 20.0E-3
    i = ii_hi[int(cft.p.x_bounds[0]/delta_t):int((cft.p.x_bounds[-1] + 2*sig_len)/delta_t)]
    t_array_i = time[int(cft.p.x_bounds[0]/delta_t):int((cft.p.x_bounds[-1] + 2*sig_len)/delta_t)]

    plt.plot(i)
    plt.plot(cft.i)
    plt.show()

    i_r = cft.i - i[0:len(cft.i)]

    ### Smooth out the signal using a Savitzky-Golay filter
    #~ from scipy.signal import savgol_filter
    #~ i_r = savgol_filter(i_r, 9, 5)
    #~
    #~ delta_t = np.diff(cft.t)[0]
    #~ di = np.gradient(cft.i, delta_t)
    #~
    #~ dt = 8E-6
    #~ di_factor = 8E-8
    #~
    #~ figg = plt.figure()
    #~ figg.suptitle('UF %s-%s RS%d' % (eventName[:2], eventName[2:], rs), fontsize=20)
    #~ axx = figg.add_subplot(111)
    #~ axx.plot(cft.t*1E6, di*di_factor, label='dI/dt')
    #~ #axx.plot((cft.t[int(dt/delta_t):]-dt)*1E6, i_r[int(dt/delta_t):], label='Reflection')
    #~ axx.plot((cft.t)*1E6, i_r, label='Reflection')
    #~ axx.set_title('Reflection and dI/dt')
    #~ axx.set_xlim([0,100])
    #~ axx.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ axx.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ axx.grid(True, which='both')
    #~
    #~ plt.legend()

    """
    For SPICE currents
    """
    #~ i = II_HI.data[int(dc.x_bounds[0]/delta_t):int(dc.x_bounds[-1]/delta_t)] - dc.DCoffset#cft.i
    #~ t_array_i = II_HI.dataTime[int(dc.x_bounds[0]/delta_t):int(dc.x_bounds[-1]/delta_t)] - II_HI.dataTime[int(dc.x_bounds[0]/delta_t)]#cft.t
    #~ with open('./I_model_normal.txt', 'w') as f:
        #~ for x in range(i.shape[0]):
            #~ f.write("%0.10f %0.10f\r\n" %(t_array_i[x],i[x]))

    #~ i = II_HI.data-dc.DCoffset
    #~ t_array_i = II_HI.dataTime-df32_tStart


    """
    Plot all currents
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3,1, sharex=True)
    fig.suptitle('UF %s-%s RS%d' % (eventName[:2], eventName[2:], rs), fontsize=20)
    ax1.plot(t_array_i*1E6,i)
    ax1.set_ylabel('A')
    ax1.set_title('II_HI')
    ax1.set_xlim([0,100])
    ax1.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.grid(True, which='both')

    ax2.plot(cft.t*1E6, cft.i)
    ax2.set_ylabel('A')
    ax2.set_title(r'Fitted II_HI ($\tau$ = %0.2e)' % tau)
    ax2.set_xlim([0,100])
    ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.grid(True, which='both')

    ax3.plot(cft.t[0:len(i_r)]*1E6, i_r)
    ax3.set_ylabel('A')
    ax3.set_xlabel('Time ($\mu$s)')
    ax3.set_title('Reflection')
    ax3.set_xlim([0,100])
    ax3.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.grid(True, which='both')

    fig1 = plt.figure()
    fig1.suptitle('UF %s-%s RS%d' % (eventName[:2], eventName[2:], rs), fontsize=20)
    ax4 = fig1.add_subplot(111)
    ax4.plot(t_array_i*1E6,i, 'b', label='II_HI')
    ax4.plot(cft.t*1E6, cft.i,'g', label=r'Fit ($\tau$ = %0.2e)' % tau)
    ax4.plot(cft.t[0:len(i_r)]*1E6, i_r, 'r', label='Reflection')
    ax4.plot(cft.t[cft.ind]*1E6, cft.i[cft.ind],'x')
    ax4.set_ylabel('A')
    ax4.set_xlabel('Time ($\mu$s)')
    ax4.set_title('Currents')
    ax4.set_xlim([0,100])
    ax4.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax4.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax4.grid(True, which='both')

    plt.legend()
    plt.show()


    """
    Save Data
    """
    data = {}

    data['i_model'] = cft.i
    data['time'] = cft.t
    data['i_r'] = i_r
    data['ii_hi'] = i
    data['tau'] = tau
    #~ data['di'] = di
    #~ data['di_factor'] = di_factor
    data['ind'] = cft.ind

    fileSave = './DataFiles/%s_I_RS%d.p' % (eventNamef, rs)
    pickle.dump(data, open(fileSave, "wb"))

    #~
    #~ plt.plot(cft.t, cft.i)

    #~ p = df.RelativeTimePlot(II_HI.dataTime-df32_tStart, II_HI.data-dc.DCoffset)
    #~ p.plot()
    #~ plt.show()
    #~
    #~ fig, ax = p.relative_plot(1E6)
    #~ ax.set_xlabel('Time ($\mu$sec)')
    #~ ax.set_ylabel('I (A)')
    #~ ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    #~ ax.grid(True, which='both')
    #~
    #~ plt.show()
