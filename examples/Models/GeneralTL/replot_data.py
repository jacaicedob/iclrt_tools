#!/usr/bin/env python

import sys
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/')
sys.path.append('/home/jaime/Documents/Python Code/Pyplot/dfplots/')

import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import operator

import iclrt_tools.plotting.dfplots as df

def moving_average(y, n=5):
    weights = np.repeat(1.0, n)/n
    sma = np.convolve(y, weights, 'same')
    return sma

c = 3.0E8

eventDate = '061809'
eventName = '0920'
eventRS = 3
dist = 92.0
# dist = 257.0
# dist = 326.0
# dist = 316.0
# dist = 181.0
# dist = 42.0E3
ttype = 'measured'

runs = None
run_data = {}

if dist == 92.0:
    measured_key = 'E_5'
    measured_dE_key = 'dE_11' # Not co-located
    dE_mult = 1.0
    measured_mult = 0.95
    runs = [1,2,3,4,5,6,7,8]
    runs = [7]
    runs = [14,7,15] # TL, MTLE, and MTLL 
    runs = [7,15,16,17]
    runs = [18]
    
elif dist == 257.0:
    measured_key = 'E_23'
    measured_dE_key = 'dE_8' # Not co-located
    dE_mult = 4.0
    measured_mult = 0.3
    runs = [9,10]
    runs = [10]
    
elif dist == 326.0:
    measured_key = 'E_18'
    measured_dE_key = 'dE_11' # Not co-located
    dE_mult = 2.6
    measured_mult = 1.3
    runs = [11]
    
elif dist == 316.0:
    measured_key = 'E_18' # Not co-located
    measured_dE_key = 'dE_11'
    dE_mult = 2.6
    measured_mult = 1.3 # Not correct
    runs = [12]
    
elif dist == 181.0:
    measured_key = 'E_18' # Not co-located
    measured_dE_key = 'dE_8'
    dE_mult = 2.6
    measured_mult = 1.3 # Not correct
    runs = [13]

elif dist == 42.0E3:
    measured_key = 'E_LOG'
    measured_dE_key = 'dE_LOG'
    dE_mult = 1.0
    measured_mult = 1.0
    runs = [18]

for run in runs:
    key = '%d' % run 
    
    E_es = {}
    E_ind = {}
    E_rad = {}
    E_tot = {}
    t_array = {}
    D = {}
    v = {}
    Ht = {}
    i = {}
    i_array = {}
    di_array = {}
    z_array = {}
    lmb = {}
    
    #~ fileName = './UF%s-RS%s-%dm/data_RS.p' % (eventName, eventRS, dist)
    fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF%sRS%d/Run%02d/data_RS.p' % (eventName, eventRS, run)

    data = pickle.load(open(fileName, 'rb'))
        
    E_es['rs'] = data['E_es']
    E_ind['rs'] = data['E_ind'] 
    E_rad['rs'] = data['E_rad']
    E_tot['rs'] = data['E']
    t_array['rs'] = data['time']
    D['rs'] = data['D']
    v['rs'] = data['v']
    #~ vr['rs'] = data['vr']
    #~ Ht['rs'] = data['Ht']
    #~ dz['rs'] = data['dz']
    i['rs'] = data['i']
    i_array['rs'] = data['i_array']
    di_array['rs'] = data['di_array']
    z_array['rs'] = data['z_array']
    lmb['rs'] = data['lmb']
    
    #~ fileName = './UF%s-RS%s-%dm/data_up.p' % (eventName, eventRS, dist)
    fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF%sRS%d/Run%02d/data_up.p' % (eventName, eventRS, run)

    data = pickle.load(open(fileName, 'rb'))
        
    E_es['up'] = data['E_es']
    E_ind['up'] = data['E_ind'] 
    E_rad['up'] = data['E_rad']
    E_tot['up'] = data['E']
    t_array['up'] = data['time']
    D['up'] = data['D']
    v['up'] = data['v']
    #~ vr['up'] = data['vr']
    #~ Ht['up'] = data['Ht']
    #~ dz['up'] = data['dz']
    #~ i['up'] = data['i']
    i_array['up'] = data['i_array']
    di_array['up'] = data['di_array']
    z_array['up'] = data['z_array']
    lmb['up'] = data['lmb']

    #~ print(np.diff(t_array)[0])

    #~ fileName = './UF%s-RS%s-%dm/data_down.p' % (eventName, eventRS, dist)
    fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF%sRS%d/Run%02d/data_down.p' % (eventName, eventRS, run)

    data = pickle.load(open(fileName, 'rb'))
        
    E_es['down'] = data['E_es']
    E_ind['down'] = data['E_ind'] 
    E_rad['down'] = data['E_rad']
    E_tot['down'] = data['E']
    t_array['down'] = data['time']
    D['down'] = data['D']
    v['down'] = data['v']
    #~ vr['down'] = data['vr']
    #~ Ht['down'] = data['Ht']
    #~ dz['down'] = data['dz']
    #~ i['down'] = data['i']
    i_array['down'] = data['i_array']
    di_array['down'] = data['di_array']
    z_array['down'] = data['z_array']
    lmb['down'] = data['lmb']
    
     #~ fileName = './UF%s-RS%s-%dm/data_Ref.p' % (eventName, eventRS, dist)
    fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF%sRS%d/Run%02d/data_Ref.p' % (eventName, eventRS, run)

    data = pickle.load(open(fileName, 'rb'))
        
    E_es['ref'] = data['E_es']
    E_ind['ref'] = data['E_ind'] 
    E_rad['ref'] = data['E_rad']
    E_tot['ref'] = data['E']
    t_array['ref'] = data['time']
    D['ref'] = data['D']
    v['ref'] = data['v']
    #~ vr['ref'] = data['vr']
    #~ Ht['ref'] = data['Ht']
    #~ dz['ref'] = data['dz']
    #~ i['ref'] = data['i']
    i_array['ref'] = data['i_array']
    di_array['ref'] = data['di_array']
    z_array['ref'] = data['z_array']
    lmb['ref'] = data['lmb']

    # fileName = './UF%s-RS%s-%dm/UF%s_I_RS%d_results_%dm_%s.p' % (eventName, eventRS, dist, eventName, eventRS, dist, ttype)
    # fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/OldCode_02182015/UF0920_I_RS3_results_%dm_measured.p' % (dist)
    #
    # data = pickle.load(open(fileName, 'rb'))
    #
    # E_es['other_model'] = data['E_es']
    # E_ind['other_model'] = data['E_ind']
    # E_rad['other_model'] = data['E_rad']
    # E_tot['other_model'] = data['E']
    # t_array['other_model'] = data['time']
    # D['other_model'] = data['D']
    # v['other_model'] = data['v']
    # #~ vr['other_model'] = data['vr']
    # #~ Ht['other_model'] = data['Ht']
    # #~ dz['other_model'] = data['dz']
    # #~ i['other_model'] = data['i']
    # i_array['other_model'] = data['i_array']
    # di_array['other_model'] = data['di_array']
    # z_array['other_model'] = data['z_array']
    # lmb['other_model'] = data['lmb']

    #~ fileName = './UF0920_data_061809_rs3.p'
    fileName = '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0920_data_061809_rs3.p'

    data = pickle.load(open(fileName, 'rb'))
        
    E_tot['measured'] = data[measured_key]['data'] 
    t_array['measured'] = data['time']
    #~ D5 = data['D']
    i['measured'] = data['II_HI']['data']
    i_array['measured'] = data['II_HI']['data']
    t_array['dE_measured'] = data[measured_dE_key]['time']
    E_tot['dE_measured'] = data[measured_dE_key]['data']
    
    ### Add up all the waves
    E_ess = E_es['rs'] + E_es['up'] + E_es['down'] + E_es['ref']
    E_indd = E_ind['rs'] + E_ind['up'] + E_ind['down'] + E_ind['ref']
    E_radd = E_rad['rs'] + E_rad['up'] + E_rad['down'] + E_rad['ref']
    E_tott = E_tot['rs'] + E_tot['up'] + E_tot['down'] + E_tot['ref']
    t_arrayy = t_array['rs']
    
    E_es['sum'] = E_ess
    E_ind['sum'] = E_indd
    E_rad['sum'] = E_radd
    E_tot['sum'] = E_tott
    t_array['sum'] = t_arrayy
    
    run_data[key] = {}
    run_data[key]['E_es'] = E_es
    run_data[key]['E_ind'] = E_ind
    run_data[key]['E_rad'] = E_rad
    run_data[key]['E_tot'] = E_tot
    run_data[key]['t_array'] = t_array
    run_data[key]['D'] = D
    run_data[key]['v'] = v
    run_data[key]['Ht'] = Ht
    run_data[key]['i'] = i
    run_data[key]['i_array'] = i_array
    run_data[key]['di_array'] = di_array
    run_data[key]['z_array'] = z_array
    run_data[key]['lmb'] = lmb
    
"""
Plots for individual files
"""
xlabel = r'Time (microseconds)'
xfactor = 1E6

ylabel = 'E-field (kV/m)'
yfactor = 1E-3

xlim = [-2,15]
#~ ylim = [0, 15]

sup_title = 'UF %s-%s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

### E_tot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(run_data['%d'%runs[0]]['t_array']['measured'], run_data['%d'%runs[0]]['E_tot']['measured']*yfactor*measured_mult, label='Measured')#r'$E^{meas}_{tot}$')
#~ ax.plot(run_data['%d'%runs[0]]['t_array']['other_model']*xfactor, run_data['%d'%runs[0]]['E_tot']['other_model']*yfactor, label=r'$E^{CALC}_{tot}$')

for run in runs:
    ave = moving_average(run_data['%d'%run]['E_tot']['sum'], 5)
    label = 'MTLE'
    
    ### Only for comparing TL, MTLE, and MTLL. Comment out otherwise
    if run == 7:
        label = r'MTLE Model, $\lambda$ = 3km'
    elif run == 14:
        label = 'TL Model'
    elif run == 15:
        label = 'MTLL Model, H = 2km'
    elif run == 16:
        label = 'MTLL Model, H = 7.5km'
    elif run == 17:
        label = r'MTLE Model, $\lambda$ = 10km'
    ###
        
    ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor, ave*yfactor, '-', label=label)#r'$E^{MTLE}_{tot}$')# -- Run %02d' % run)
    
ax.set_title(sup_title)
#~ ax.set_xlabel(xlabel)
#~ ax.set_ylabel(ylabel)
ax.set_xlim(xlim)
ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.grid(True,which='both')
ax.legend(loc=4)

p = df.pickerPlot(fig, ax)
p.plot()

### dE/dt
dE = np.gradient(run_data['%d'%runs[0]]['E_tot']['sum'], np.diff(run_data['%d'%run]['t_array']['rs'])[0])
boost = dE_mult
ylim = [-2, 16]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title(sup_title + ' -- dE/dt (D = %0.1f m)' % dist)
ax.plot(run_data['%d'%run]['t_array']['dE_measured'], moving_average(run_data['%d'%run]['E_tot']['dE_measured'],30)*1E-9, label=r'Measured')
ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor,moving_average(dE,5)*boost*1E-9, label=r'MTLE $\times$ %0.2f' % boost)

ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
ax.grid(True, which='both')
ax.legend()

p = df.pickerPlot(fig, ax)
p.plot()

#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot(t_array2*xfactor, (E_es2)*yfactor,label=r'$E^{CALC}_{es}$')
#~ ax.plot(t_arrayy*xfactor, (E_ess)*yfactor, '--', label=r'$E^{sum}_{es}$')
#~ ax.set_title(sup_title)
#~ #ax.set_xlabel(xlabel)
#~ #ax.set_ylabel(ylabel)
#~ ax.set_xlim(xlim)
#~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ #ax.grid(True,which='both')
#~ ax.legend(loc=5)
#~ 
#~ fig = plt.figure()
#~ 
#~ ax = fig.add_subplot(111)
#~ ax.plot(t_array2*xfactor, (E_ind2)*yfactor, label=r'$E^{CALC}_{ind}$')
#~ ax.plot(t_arrayy*xfactor, (E_indd)*yfactor, '--', label=r'$E^{sum}_{ind}$')
#~ ax.set_title(sup_title)
#~ #ax.set_xlabel(xlabel)
#~ #ax.set_ylabel(ylabel)
#~ ax.set_xlim(xlim)
#~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ #ax.grid(True,which='both')
#~ ax.legend()
#~ 
#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.plot(t_array2*xfactor, (E_rad2)*yfactor, label=r'$E^{CALC}_{rad}$')
#~ ax.plot(t_arrayy*xfactor, (E_radd)*yfactor, '--', label=r'$E^{sum}_{rad}$')
#~ ax.set_title(sup_title)
#~ #ax.set_xlabel(xlabel)
#~ #ax.set_ylabel(ylabel)
#~ ax.set_xlim(xlim)
#~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ #ax.grid(True,which='both')
#~ ax.legend()
#~ 
#~ fig = plt.figure()
#~ ax = fig.add_subplot(111)
#~ ax.set_title(sup_title)
#~ 
#~ Hr = 0

#~ i_1r = run_data['%d' % runs[0]]['i_array']['other_model'][:,Hr]
#~ i_general = run_data['%d' % runs[0]]['i_array']['rs'][:,Hr] + run_data['%d' % runs[0]]['i_array']['down'][:,Hr] + run_data['%d' % runs[0]]['i_array']['ref'][:,Hr]
#~ 
#~ ax.plot(run_data['%d' % runs[0]]['t_array']['measured'], run_data['%d' % runs[0]]['i_array']['measured']*yfactor, label='Measured')
#~ 
#~ ax.plot(run_data['%d' % runs[0]]['t_array']['rs']*xfactor, i_general*yfactor, '--' , label='MTLE')

#ax.plot(run_data['%d' % runs[0]]['t_array']['other_model']*xfactor, i_1r*yfactor, '-x', label='1 Reflection')

#ax.plot(run_data['%d' % runs[0]]['t_array']['ref']*xfactor, run_data['%d' % runs[0]]['i_array']['ref'][:,Hr]*yfactor, label='GND Reflection')

#ax.plot(run_data['%d' % runs[0]]['t_array']['up']*xfactor, run_data['%d' % runs[0]]['i_array']['up'][:,Hr]*yfactor, label='Up')

#ax.plot(run_data['%d' % runs[0]]['t_array']['down']*xfactor, run_data['%d' % runs[0]]['i_array']['down'][:,Hr]*yfactor, label='Down')



#ax.plot(run_data['%d' % runs[0]]['t_array']['rs']*xfactor, run_data['%d' % runs[0]]['i_array']['rs'][:,Hr]*yfactor, label='I RS')

#ax.plot(run_data['%d' % runs[0]]['t_array']['rs']*xfactor, run_data['%d' % runs[0]]['i']['rs'][0:int(len(run_data['%d' % runs[0]]['t_array']['rs']))]*yfactor, label='I input')


#~ ax.set_xlim(xlim)
#~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
#~ ax.grid(True,which='both')
#~ ax.legend()
#~ p = df.pickerPlot(fig,ax)
#~ p.plot()

for run in runs:
    
    boost = 5.0
    
    #### Comment out to plot these figures
    #~ if True:
        #~ break;
    ####
    
    #~ sup_title = 'UF %s-%s: RS %d -- Run %02d' % (eventName[:2], eventName[2:], eventRS, run)
    
    sup_title = 'UF %s-%s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

    ### Only for comparing TL, MTLE, and MTLL. Comment out otherwise
    if run == 7:
        sup_title += r'MTLE Model, $\lambda$ = 3km'
    elif run == 14:
        sup_title += 'TL Model'
    elif run == 15:
        sup_title += 'MTLL Model, H = 2km'
    elif run == 16:
        sup_title += 'MTLL Model, H = 7.5km'
    elif run == 17:
        sup_title += r'MTLE Model, $\lambda$ = 10km'
    ###

    ### E_tot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor, run_data['%d' % run]['E_tot']['sum']*yfactor, label=r'$E_{Total}$')#r'$E^{sum}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor, run_data['%d' % run]['E_tot']['rs']*yfactor, '+', label=r'$E_{RS}$')#r'$E^{RS}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['up']*xfactor, run_data['%d' % run]['E_tot']['up']*yfactor*boost, '--', label=r'$E_{UP} \times$ %d' % boost)#r'$E^{UP}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['down']*xfactor, run_data['%d' % run]['E_tot']['down']*yfactor*boost, '--', label=r'$E_{DOWN} \times$ %d' % boost)#r'$E^{DOWN}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor, run_data['%d' % run]['E_tot']['ref']*yfactor*boost, '+', label=r'$E_{REF} \times$ %d' % boost)#r'$E^{REF}_{tot}$')
    # ax.plot(t_array['up']*xfactor, (E_tot['up']+E_tot['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{tot}$')
    ax.set_title(sup_title)
    # ax.set_xlabel(xlabel)
    # ax.set_ylabel(ylabel)
    ax.set_xlim(xlim)
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(True,which='both')
    # ax.legend(loc=5)
    
    p = df.pickerPlot(fig, ax)
    p.plot()
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor, run_data['%d' % run]['E_tot']['sum']*yfactor, label=r'$E_{Total}$')#r'$E^{sum}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor, run_data['%d' % run]['E_tot']['rs']*yfactor, '+', label=r'$E_{RS}$')#r'$E^{RS}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['up']*xfactor, run_data['%d' % run]['E_tot']['up']*yfactor*boost, '--', label=r'$E_{UP} \times$ %d' % boost)#r'$E^{UP}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['down']*xfactor, run_data['%d' % run]['E_tot']['down']*yfactor*boost, '--', label=r'$E_{DOWN} \times$ %d' % boost)#r'$E^{DOWN}_{tot}$')
    ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor, run_data['%d' % run]['E_tot']['ref']*yfactor*boost, '+', label=r'$E_{REF} \times$ %d' % boost)#r'$E^{REF}_{tot}$')
    # ax.plot(t_array['up']*xfactor, (E_tot['up']+E_tot['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{tot}$')
    ax.set_title(sup_title)
    # ax.set_xlabel(xlabel)
    # ax.set_ylabel(ylabel)
    ax.set_xlim(xlim)
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(True,which='both')
    ax.legend(loc=5)

    ### E_es
    #~ fig = plt.figure()
    #~ ax = fig.add_subplot(111)
    #~ ax.plot(t_arrayy*xfactor, E_ess*yfactor, label=r'$E^{sum}_{es}$')
    #~ ax.plot(t_array['rs']*xfactor, E_es['rs']*yfactor, '+', label=r'$E^{RS}_{es}$')
    #~ ax.plot(t_array['up']*xfactor, E_es['up']*yfactor, '--', label=r'$E^{UP}_{es}$')
    #~ ax.plot(t_array['down']*xfactor, E_es['down']*yfactor, '--', label=r'$E^{DOWN}_{es}$')
    #~ ax.plot(t_array['ref']*xfactor, E_es['ref']*yfactor, '+', label=r'$E^{REF}_{es}$')
    #~ # ax.plot(t_array['up']*xfactor, (E_es['up']+E_es['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{es}$')
    #~ ax.set_title(sup_title)
    #~ # ax.set_xlabel(xlabel)
    #~ # ax.set_ylabel(ylabel)
    #~ ax.set_xlim(xlim)
    #~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ #ax.grid(True,which='both')
    #~ ax.legend(loc=5)

    ### E_ind
    #~ fig = plt.figure()
    #~ ax = fig.add_subplot(111)
    #~ ax.plot(t_arrayy*xfactor, E_indd*yfactor,label=r'$E^{sum}_{ind}$')
    #~ ax.plot(t_array['rs']*xfactor, E_ind['rs']*yfactor, '+', label=r'$E^{RS}_{ind}$')
    #~ ax.plot(t_array['up']*xfactor, E_ind['up']*yfactor, '--', label=r'$E^{UP}_{ind}$')
    #~ ax.plot(t_array['down']*xfactor, E_ind['down']*yfactor, '--', label=r'$E^{DOWN}_{ind}$')
    #~ ax.plot(t_array['ref']*xfactor, E_ind['ref']*yfactor, '+', label=r'$E^{REF}_{ind}$')
    #~ # ax.plot(t_array['up']*xfactor, (E_ind['up']+E_ind['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{ind}$')
    #~ ax.set_title(sup_title)
    #~ # ax.set_xlabel(xlabel)
    #~ # ax.set_ylabel(ylabel)
    #~ ax.set_xlim(xlim)
    #~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ #ax.grid(True,which='both')
    #~ ax.legend()

    ### E_rad
    #~ fig = plt.figure()
    #~ ax = fig.add_subplot(111)
    #~ ax.plot(t_arrayy*xfactor, E_radd*yfactor, label=r'$E^{sum}_{rad}$')
    #~ ax.plot(t_array['rs']*xfactor, E_rad['rs']*yfactor, '+', label=r'$E^{RS}_{rad}$')
    #~ ax.plot(t_array['up']*xfactor, E_rad['up']*yfactor, '--', label=r'$E^{UP}_{rad}$')
    #~ ax.plot(t_array['down']*xfactor, E_rad['down']*yfactor, '--', label=r'$E^{DOWN}_{rad}$')
    #~ ax.plot(t_array['ref']*xfactor, E_rad['ref']*yfactor, '+', label=r'$E^{REF}_{rad}$')
    #~ # ax.plot(t_array['up']*xfactor, (E_rad['up']+E_rad['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{rad}$')
    #~ ax.set_title(sup_title)
    #~ # ax.set_xlabel(xlabel)
    #~ # ax.set_ylabel(ylabel)
    #~ ax.set_xlim(xlim)
    #~ ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    #~ #ax.grid(True,which='both')
    #~ ax.legend()
    
plt.show()
