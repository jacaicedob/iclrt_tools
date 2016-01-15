#!/usr/bin/env python

import dfplots as df
import lecroy as lc
import Yoko750 as yk750
import Yoko850 as yk850

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import scipy.integrate as integrate
from scipy.signal import savgol_filter

import sys
import pickle
import operator


def main():
    eventDate = '081713'
    eventName = '1333'
    rs = 1
    
    scope18_number = 1
    scope20_number = 2
    scope21_number = 2
    scope24_number = 1
    scope25_number = 3
    scope26_number = 1
    
    meas_numbers = [scope18_number, scope20_number, scope21_number, scope24_number,scope25_number, scope26_number]
    
    #~ get_data_set(eventDate, eventName, meas_numbers, rs)
    plot_data_set(eventDate, eventName, rs)

def get_data_set(eventDate=1, eventName = '0000', meas_numbers=[], rs = 1):
    
    """
    File Information
    """

    eventDate = eventDate
    eventName = eventName
    rs = rs
    
    if meas_numbers == []:
        scope18_number = 0
        scope20_number = 0
        scope21_number = 0
        scope24_number = 0
        scope25_number = 0
        scope26_number = 0
    else:
        scope18_number = meas_numbers[0]
        scope20_number = meas_numbers[1]
        scope21_number = meas_numbers[2]
        scope24_number = meas_numbers[3]
        scope25_number = meas_numbers[4]
        scope26_number = meas_numbers[5]
    
    # Scope filenames
    scope24_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope24/D000%d' % (eventDate, scope24_number)
    
    scope25_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope25/D000%d' % (eventDate, scope25_number)
    
    scope26_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope26/C1AC0000%d.trc' % (eventDate, scope26_number)
    
    log_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/LOG/Data for Jaime/UF13-09/UF1309_LOG_E'
    
    # Scope 20
    de_1_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C1AC0000%d.trc' % (eventDate, scope20_number)
    de_3_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C2AC0000%d.trc' % (eventDate, scope20_number)
    de_4_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C3AC0000%d.trc' % (eventDate, scope20_number)
    de_5_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C4AC0000%d.trc' % (eventDate, scope20_number)
    
    # Scope 21
    de_7_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C1AC0000%d.trc' % (eventDate, scope21_number)
    de_8_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C2AC0000%d.trc' % (eventDate, scope21_number)
    de_9_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C3AC0000%d.trc' % (eventDate, scope21_number)
    de_11_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope20/C4AC0000%d.trc' % (eventDate, scope21_number)
    
    # Scope 18
    de_17_filename = '/media/jaime/JaimeBackup/OSX2/My Papers/Current Reflections/Raw Data/%s/Scope18/C4AC0000%d.trc' % (eventDate, scope18_number)

    # Measurement parameters
    II_HI_24 = {'cal':55214.78, 'trace':1, 'fileName':scope24_filename, 'units':'A', 'distance':'0m'}
    II_HI = {'cal':19960.08, 'trace':13, 'fileName':scope25_filename, 'units':'A', 'distance':'0m'}
    II_HI_26 = {'cal':59127.23, 'trace':5, 'fileName':scope26_filename, 'units':'A', 'distance':'0m'}
    
    E_7 = {'cal':75.82, 'trace':2, 'fileName':scope25_filename, 'units':'V/m', 'distance':'225m'}
    E_12F = {'cal':61721.9, 'trace':3, 'fileName':scope25_filename, 'units':'V/m', 'distance':'180m'}
    E_12 = {'cal':200384.89, 'trace':4, 'fileName':scope25_filename, 'units':'V/m', 'distance':'180m'}
    E_13 = {'cal':67.2, 'trace':5, 'fileName':scope25_filename, 'units':'V/m', 'distance':'26m'}
    E_13F = {'cal':23.64, 'trace':6, 'fileName':scope25_filename, 'units':'V/m', 'distance':'26m'}
    E_NW60 = {'cal':8387.2, 'trace':7, 'fileName':scope25_filename, 'units':'V/m', 'distance':'60m'}
    E_NW100 = {'cal':8074.52, 'trace':8, 'fileName':scope25_filename, 'units':'V/m', 'distance':'100m'}
    E_16HI = {'cal':16555.67, 'trace':9, 'fileName':scope25_filename, 'units':'V/m', 'distance':'65m'}
    E_16LO = {'cal':3050.02, 'trace':10, 'fileName':scope25_filename, 'units':'V/m', 'distance':'63m'}
    
    E_5 = {'cal':30904.17, 'trace':14, 'fileName':scope24_filename, 'units':'V/m', 'distance':'92m'}
    E_11 = {'cal':2436.68, 'trace':7, 'fileName':scope24_filename, 'units':'V/m', 'distance':'316m'}
    E_18 = {'cal':23647.60, 'trace':8, 'fileName':scope24_filename, 'units':'V/m', 'distance':'327m'}
    E_23 = {'cal':40482.39, 'trace':10, 'fileName':scope24_filename, 'units':'V/m', 'distance':'257m'}

    E_LOG = {'cal':100, 'trace':1, 'fileName':log_filename, 'units':'V/m', 'distance':'45km'}
    
    dE_1  = {'cal':15.76*1E9, 'trace':1, 'fileName':de_1_filename, 'units':'V/m/s', 'distance':'165m'}
    dE_3  = {'cal':15.65*1E9, 'trace':1, 'fileName':de_3_filename, 'units':'V/m/s', 'distance':'137m'}
    dE_4  = {'cal':14.89*1E9, 'trace':1, 'fileName':de_4_filename, 'units':'V/m/s', 'distance':'382m'}
    dE_5  = {'cal':15.14*1E9, 'trace':1, 'fileName':de_5_filename, 'units':'V/m/s', 'distance':'77m'}
    
    dE_7  = {'cal':14.33*1E9, 'trace':1, 'fileName':de_7_filename, 'units':'V/m/s', 'distance':'225m'}
    dE_8  = {'cal':13.44*1E9, 'trace':1, 'fileName':de_8_filename, 'units':'V/m/s', 'distance':'313m'}
    dE_9  = {'cal':14.20*1E9, 'trace':1, 'fileName':de_9_filename, 'units':'V/m/s', 'distance':'390m'}
    dE_11  = {'cal':14.24*1E9, 'trace':1, 'fileName':de_11_filename, 'units':'V/m/s', 'distance':'233m'}
    
    dE_17  = {'cal':14.58*1E9, 'trace':1, 'fileName':de_17_filename, 'units':'V/m/s', 'distance':'27m'}
    
    
    scope24_meas = {}#'II_HI':II_HI_24, \
                    #~ 'E_5':E_5, \
                    #~ 'E_11':E_11, \
                    #~ 'E_18':E_18, \
                    #~ 'E_23':E_23 , \
                    #~ }
    
    scope25_meas = {'II_HI':II_HI, \
                    'E_12F':E_12F , \
                    #~ 'E_12':E_12, \
                    #~ # 'E_13':E_13, \
                    #~ # 'E_13F':E_13F, \
                    'E_NW60':E_NW60, \
                    #~ 'E_NW100':E_NW100, \
                    #~ 'E_16HI':E_16HI\
                    'E_16LO':E_16LO, \
                    }
                     
    scope20_meas = {'dE_1':dE_1, \
                    'dE_3':dE_3, \
                    'dE_4':dE_4, \
                    'dE_5':dE_5, \
                   }
                   
    scope21_meas = {'dE_7':dE_7, \
                    'dE_8':dE_8, \
                    'dE_9':dE_9, \
                    'dE_11':dE_11, \
                   }
                   
    scope26_meas = {}#'II_HI':II_HI_26}
    
    scope18_meas = {'dE_17':dE_17}
    
    log_meas = {}#'E_LOG':E_LOG}

    t_start = 0
    t_end = 2
    wantOffset = False

    """
    Load waveforms
    """
    ### II_HI
    
    keys = scope24_meas.keys()
    
    if keys:
        f = yk850.Yoko850File(scope24_filename)
        header = f.get_header()
        
        result = {}
    
    for i,key in enumerate(keys):
        try:
            result[key] = f.get_trace_data(header, scope24_meas[key]['trace'], t_start,\
                            t_end, scope24_meas[key]['cal'], wantOffset)
        except AttributeError:
            print("\n\nERROR: Invalid file.")
            sys.exit(1)
            
    for i,key in enumerate(keys):
        scope24_meas[key]['result'] = result[key]
    
    keys = scope25_meas.keys()
    
    if keys:
        f = yk850.Yoko850File(scope25_filename)
        header = f.get_header()
        
        result = {}
    
    for i,key in enumerate(keys):
        try:
            result[key] = f.get_trace_data(header, scope25_meas[key]['trace'], t_start,\
                            t_end, scope25_meas[key]['cal'], wantOffset)
        except AttributeError:
            print("\n\nERROR: Invalid file.")
            sys.exit(1)
            
    for i,key in enumerate(keys):
        scope25_meas[key]['result'] = result[key]
        
    keys = scope26_meas.keys()
    
    for i,key in enumerate(keys):
        lecroy = lc.lecroy_data(scope26_meas[key]['fileName'])
        lecroy.get_seg_time()
        lecroy.get_segment(scope26_meas[key]['trace'], scope26_meas[key]['cal'])
        offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
        lecroy.data -= offset
        
        scope26_meas[key]['result'] = lecroy        
        
    
    ### E_LOG
    f = yk850.Yoko850File(log_filename)
    header = f.get_header()
    
    keys = log_meas.keys()
    result = {}
    
    for i,key in enumerate(keys):
        try:
            result[key] = f.get_trace_data(header, log_meas[key]['trace'], 2.4,\
                            2.7, log_meas[key]['cal'], wantOffset)
        except AttributeError:
            print("\n\nERROR: Invalid file.")
            sys.exit(1)
            
    for i,key in enumerate(keys):
        log_meas[key]['result'] = result[key]


    ### dE/dt
    keys = scope20_meas.keys()
    
    for i,key in enumerate(keys):
        lecroy = lc.lecroy_data(scope20_meas[key]['fileName'])
        lecroy.get_seg_time()
        lecroy.get_segment(scope20_meas[key]['trace'], scope20_meas[key]['cal'])
        offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
        lecroy.data -= offset
        
        scope20_meas[key]['result'] = lecroy    
        
        dt = np.diff(lecroy.dataTime)[0]
        ind = 0 #len(lecroy.dataTime)/2.0 - 100E-6/dt 
        
        scope20_meas[key]['result'].data = integrate.cumtrapz(y=scope20_meas[key]['result'].data[ind:], x=scope20_meas[key]['result'].dataTime[ind:], initial=0)
        scope20_meas[key]['result'].dataTime = scope20_meas[key]['result'].dataTime[ind:]
        
    keys = scope21_meas.keys()
    
    for i,key in enumerate(keys):
        lecroy = lc.lecroy_data(scope21_meas[key]['fileName'])
        lecroy.get_seg_time()
        lecroy.get_segment(scope21_meas[key]['trace'], scope21_meas[key]['cal'])
        offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
        lecroy.data -= offset
        
        scope21_meas[key]['result'] = lecroy   
        
        dt = np.diff(lecroy.dataTime)[0]
        ind = 0 #len(lecroy.dataTime)/2.0 - 100E-6/dt     
        
        scope21_meas[key]['result'].data = integrate.cumtrapz(y=scope21_meas[key]['result'].data[ind:], x=scope21_meas[key]['result'].dataTime[ind:], initial=0)
        scope21_meas[key]['result'].dataTime = scope21_meas[key]['result'].dataTime[ind:]
        
    keys = scope18_meas.keys()
    
    for i,key in enumerate(keys):
        lecroy = lc.lecroy_data(scope18_meas[key]['fileName'])
        lecroy.get_seg_time()
        lecroy.get_segment(scope18_meas[key]['trace'], scope18_meas[key]['cal'])
        offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
        lecroy.data -= offset
        
        scope18_meas[key]['result'] = lecroy        
        
        scope18_meas[key]['result'].data = integrate.cumtrapz(y=scope18_meas[key]['result'].data, x=scope18_meas[key]['result'].dataTime, initial=0)
        
    """
    Get time intervals
    """
    rt_plots = {}
    
    keys = scope24_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope24_meas[key]['result'].dataTime, scope24_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
    
    keys = scope25_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope25_meas[key]['result'].dataTime, scope25_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
        
        print('%s offset: %02.f' % (key, rt_plots[key].y[rt_plots[key].zero_ind]))
        
    keys = scope20_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope20_meas[key]['result'].dataTime, scope20_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
        
        print('%s offset: %02.f' % (key, rt_plots[key].y[rt_plots[key].zero_ind]))
        
    keys = scope21_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope21_meas[key]['result'].dataTime, scope21_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
        
        print('%s offset: %02.f' % (key, rt_plots[key].y[rt_plots[key].zero_ind]))
        
    keys = log_meas.keys()
    
    keys = scope26_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope26_meas[key]['result'].dataTime, scope26_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
        
    keys = scope18_meas.keys()
    
    for i, key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(scope18_meas[key]['result'].dataTime, scope18_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()
        
        print('%s offset: %02.f' % (key, rt_plots[key].y[rt_plots[key].zero_ind]))
        
    keys = log_meas.keys()
    
    for i,key in enumerate(keys):
        print("Acquiring %s" % key)
        rt_plots[key] = df.RelativeTimePlot(log_meas[key]['result'].dataTime, log_meas[key]['result'].data, max_points=1E9)
        rt_plots[key].plot()
        plt.show()        

    """
    Plot
    """
    axes = {}
    lims = [5E-6,95E-6]
    
    
    for i,key in enumerate(rt_plots):
        fig, ax = rt_plots[key].relative_plot(1E6,lims)
        
        if key in list(scope24_meas.keys()):
            ax.set_title('%s (D = %s)' % (key,scope24_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope24_meas[key]['units'])
            
        elif key in list(scope25_meas.keys()):
            ax.set_title('%s (D = %s)' % (key,scope25_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope25_meas[key]['units'])
            
        elif key in list(scope20_meas.keys()):
            ax.set_title('%s (D = %s)' % ('Integrated %s'%key,scope20_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope20_meas[key]['units'])
            
        elif key in list(scope21_meas.keys()):
            ax.set_title('%s (D = %s)' % ('Integrated %s'%key,scope21_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope21_meas[key]['units'])
            
        elif key in list(scope26_meas.keys()):
            ax.set_title('%s (D = %s)' % (key,scope26_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope26_meas[key]['units'])
        
        elif key in list(scope18_meas.keys()):
            ax.set_title('%s (D = %s)' % ('Integrated %s'%key,scope18_meas[key]['distance']))
            ax.set_ylabel('(%s)' % scope18_meas[key]['units'])
        
        elif key in list(log_meas.keys()):
            ax.set_title('%s (D = %s)' % (key,log_meas[key]['distance']))
            ax.set_ylabel('(%s)' % log_meas[key]['units'])
        
        axes[key] = ax
        plt.close(fig)
        
    #~ 
    #~ for i,key in enumerate(rt_plots_l):
        #~ fig, ax = rt_plots_l[key].relative_plot(1E6,lims)
        #~ ax.set_title('%s (D = %s)' % (key,log_meas[key]['distance']))
        #~ ax.set_ylabel('(%s)' % log_meas[key]['units'])
        #~ axes[key] = ax
        #~ plt.close(fig)
        
    """
    Save data
    """
        
    keys = axes.keys()
    data = {'axes':axes}
    
    for i,key in enumerate(keys):
        if key == 'E_LOG':
            data[key] = axes[key].get_lines()[0].get_ydata() - rt_plots[key].y[(rt_plots[key].zero_time - rt_plots[key].x[0])/rt_plots[key].delta_t]
            
        else:
            print("Offsetting %s by %0.2f" % (key, rt_plots[key].y[rt_plots[key].zero_ind]))
            data[key] = axes[key].get_lines()[0].get_ydata() - rt_plots[key].y[rt_plots[key].zero_ind]
        
    data['time'] = axes['II_HI'].get_lines()[0].get_xdata()    
    

    fileSave = "UF%s_data_%s_rs%d.p" % (eventName, eventDate, rs)
    #~ fileSave = "data_test.p"
    
    try:
        fo = pickle.load(open(fileSave, "rb"))
        temp = {}
        
        for i,key in enumerate(fo.keys()):
            temp[key] = fo[key]
            
        for i,key in enumerate(axes.keys()):
            temp[key] = data[key]
            temp['axes'][key] = axes[key]
            
        pickle.dump(temp, open(fileSave, "wb"))
            
    except FileNotFoundError:
        pickle.dump(data, open(fileSave, "wb"))
    

def plot_data_set(eventDate=1, eventName='0000', rs=1):
    eventDate = eventDate
    eventName = eventName
    rs = rs
    
    fileSave = "UF%s_data_%s_rs%d.p" % (eventName, eventDate, rs)
    #~ fileSave = "data_test.p"
    data = pickle.load(open(fileSave, "rb"))
    
    event = 'UF %s-%s RS%d' % (eventName[:2], eventName[2:], rs)
    
    keys = data.keys()
    data_only = {}
    ignore = ['time', 'axes']
    
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
    
    #~ print(sorted_data)
    #~ print(data[sorted_data[0][0]])
    #~ sys.exit(1)
    
    l = int((len(list(keys)))/2)
    
    if len(list(keys)) % 2 == 1:
        l += 1
    
    fig, ax = plt.subplots(l, 2, sharex=True)
    
    fig.suptitle('%s (%s/%s/%s)' % (event, eventDate[:2],eventDate[2:4], eventDate[4:]), fontsize=16)
    #~ ax[0].plot(data['time'],data['II_HI'][::int(len(data['II_HI'])/len(data['time']))])
    #~ ax[0].set_title(data['axes']['II_HI'].get_title())
    #~ ax[0].set_ylabel(data['axes']['II_HI'].get_ylabel())
    #~ ax[0].set_xlim(data['axes']['II_HI'].get_xlim())
    
    #~ size = len(sorted_data)
    
    for i in range(len(sorted_data)):

        temp_data = data[sorted_data[i][0]][::int(len(data[sorted_data[i][0]])/len(data['time']))]
        
        zoom_lim = [-5, 20]
        
        ax[i%int(l)][int(i/l)].plot(data['time'],temp_data)
        ax[i%int(l)][int(i/l)].set_title(data['axes'][sorted_data[i][0]].get_title())
        
        ylabel = data['axes'][sorted_data[i][0]].get_ylabel()
        
        if '/s' in ylabel:
            ylabel = ylabel[:-3] + ylabel[-1]
        
        ax[i%int(l)][int(i/l)].set_ylabel(ylabel)
        ax[i%int(l)][int(i/l)].set_xlim(zoom_lim)
        ax[i%int(l)][int(i/l)].xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax[i%int(l)][int(i/l)].grid(True,which='both')
        ax[i%int(l)][int(i/l)].xaxis.set_tick_params(width=1.5)
    
    plt.xlabel('Time ($\mu$s)')
    
    fig, (ax1,ax2) = plt.subplots(2,1)
    ax1.plot(data['axes']['dE_9'].get_lines()[0].get_ydata())
    ax2.plot(data['dE_9'], 'r')

    plt.show()
    
if __name__ == "__main__":
    main()
    
    


