#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import pickle
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import JaimePackages.plotting.dfplots as df

color_cycle = ['#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854', '#4D4D4D']
color_cycle_alt = ['#B276B2', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F',  '#DECF3F', '#F15854', '#4D4D4D', '#5DA5DA']

def moving_average(y, n=5):
    weights = np.repeat(1.0, n)/n
    sma = np.convolve(y, weights, 'same')
    return sma

def plot_runs_with_measured(runs, run_data, eventName, eventRS,
                            measured_mult, xlim=[-2,25]):
    mpl.rcParams['axes.color_cycle'] = color_cycle

    xlabel = r'Time (microseconds)'
    xfactor = 1E6

    ylabel = 'E-field (kV/m)'
    yfactor = 1E-3

    # xlim = [-2,30]
    #~ ylim = [0, 15]

    xoffset = 5.0  # in usec

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(run_data['%d'%runs[0]]['t_array']['measured'],
            run_data['%d'%runs[0]]['E_tot']['measured']*yfactor,
        label='Measured')

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.plot(run_data['%d'%runs[0]]['t_array']['sum']*xfactor-xoffset, run_data['%d'%runs[0]]['i']['measured'][:len(run_data['%d'%runs[0]]['t_array']['sum'])]*yfactor, label='Measured')

    for run in runs:
        # ave = moving_average(run_data['%d'%run]['E_tot']['{0}'.format(wave)], 5)
        sup_title = r'UF %s-%s (RS #%d) - %d m' % (eventName[:2],
                                                    eventName[2:], eventRS, run_data['%d'%run]['D']['rs'])
        ave = run_data['%d'%run]['E_tot']['sum']
        label = 'MTLE'
        # label = 'Run {0}'.format(run)

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
        elif run == 19:
            label = r'$v_r = v$'
        elif run == 27:
            label = r'$v_r > v$'
            label = r'$\lambda =$ 3 km'
        elif run == 46:
            label = r'$v_r < v$'
        elif run == 47:
            label = r'$\lambda =$ 2 km'
        ###

        ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                ave*yfactor, '-', label=label)

        ax1.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                 run_data['%d'%run]['i_array']['sum'][:,0]*yfactor, '-',
                 label=label)

    ax.set_title(sup_title)
    # ax.set_xlabel(xlabel)
    # ax.set_ylabel(ylabel)
    ax.set_xlim(xlim)
    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(True,which='both')
    # ax.legend(loc=4)

    fig2 = plt.figure()
    handles, labels = ax.get_legend_handles_labels()
    fig2.legend(handles, labels)

    ax1.set_xlim(xlim)
    ax1.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.grid(True,which='both')

    p = df.pickerPlot(fig, ax)
    p.plot()

    p1 = df.pickerPlot(fig1, ax1)
    p1.plot()

def plot_runs_together(runs, run_data, waves, eventName, eventRS,
                       measured_mult, components=['tot', 'es', 'ind', 'rad'],
                       xlim=[-2,25]):
    mpl.rcParams['axes.color_cycle'] = color_cycle

    xlabel = r'Time (microseconds)'
    xfactor = 1E6

    ylabel = 'E-field (kV/m)'
    yfactor = 1E-3

    # xlim = [-2,30]
    #~ ylim = [0, 15]

    xoffset = 5.0  # in usec

    sup_title = 'UF %s-%s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

    for wave in waves:

        if 'tot' in components:
            ### E_tot
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                yfactor = 1E-3
                # ave = moving_average(run_data['%d'%run]['E_tot']['{0}'.format(wave)], 5)
                ave = run_data['%d'%run]['E_tot']['{0}'.format(wave)]
                label = r'$MTLE_{total}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                if run_data['%d'%run]['D']['rs'] == 92:
                    yfactor /= 16
                if run_data['%d'%run]['D']['rs'] == 249:
                    yfactor /= 4.1
                if run_data['%d'%run]['D']['rs'] == 500:
                    yfactor /= 1.3

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, ave*yfactor, '-', label=label)#r'$E^{MTLE}_{tot}$')# -- Run %02d' % run)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True, which='both')
            ax.legend(loc=4)
            # ax.set_yscale('log')

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'es' in components:
            ### E_es
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                # ave = moving_average(run_data['%d'%run]['E_es']['{0}'.format(wave)], 5)
                ave = run_data['%d'%run]['E_es']['{0}'.format(wave)]

                label = r'$MTLE_{es}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, ave*yfactor, '-', label=label)#r'$E^{MTLE}_{tot}$')# -- Run %02d' % run)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'ind' in components:
            ### E_ind
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                # ave = moving_average(run_data['%d'%run]['E_ind']['{0}'.format(wave)], 5)
                ave = run_data['%d'%run]['E_ind']['{0}'.format(wave)]

                label = r'$MTLE_{ind}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, ave*yfactor, '-', label=label)#r'$E^{MTLE}_{tot}$')# -- Run %02d' % run)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'rad' in components:
            ### E_rad
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                # ave = moving_average(run_data['%d'%run]['E_rad']['{0}'.format(wave)], 5)
                ave = run_data['%d'%run]['E_rad']['{0}'.format(wave)]

                label = r'$MTLE_{rad}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, ave*yfactor, '-', label=label)#r'$E^{MTLE}_{tot}$')# -- Run %02d' % run)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

def plot_runs_individually(runs, run_data, eventName, eventRS, measured_mult,
                           components=['tot', 'es', 'ind', 'rad'],
                           boost=5.0, xlim=[-2,25]):

    xlabel = r'Time (microseconds)'
    xfactor = 1E6

    ylabel = 'E-field (kV/m)'
    yfactor = 1E-3

    # xlim = [-2,30]
    #~ ylim = [0, 15]

    xoffset = 5.0  # in usec

    sup_title = 'UF %s-%s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

    for run in runs:

        #~ sup_title = 'UF %s-%s: RS %d -- Run %02d' % (eventName[:2], eventName[2:], eventRS, run)

        # sup_title = 'UF %s-%s (RS #%d) D = %d' % (eventName[:2], eventName[2:], eventRS, run_data['%d' % run]['D']['rs'])

        sup_title = 'UF %s-%s (RS #%d) -- MTLE (D = %d m)' % (eventName[:2], eventName[2:], eventRS, run_data['%d'%run]['D']['rs'])

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

        if 'tot' in components:
            mpl.rcParams['axes.color_cycle'] = color_cycle_alt

            # E_tot
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['rs']*yfactor, '--',
                    label=r'$E_{RS}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['sum']*yfactor,
                    label=r'$E_{Total}$')

            if boost == 1.0:
                label = r'$E_{UP}$'
            else:
                label = r'$E_{UP} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['up']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['up']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E_{DOWN}$'
            else:
                label = r'$E_{DOWN} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['down']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['down']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E_{REF}$'
            else:
                label = r'$E_{REF} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['ref']*yfactor*boost, '--',
                    label=label)

            # ax.plot(t_array['up']*xfactor, (E_tot['up']+
            #         E_tot['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{tot}$')

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels, loc=5)

            p = df.pickerPlot(fig, ax)
            p.plot()

            # Total fields without legend for a clean plot

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['rs']*yfactor, '--',
                    label=r'$E_{RS}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['sum']*yfactor,
                    label=r'$E_{Total}$')

            if boost == 1.0:
                label = r'$E_{UP}$'
            else:
                label = r'$E_{UP} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['up']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['up']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E_{DOWN}$'
            else:
                label = r'$E_{DOWN} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['down']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['down']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E_{REF}$'
            else:
                label = r'$E_{REF} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['ref']*yfactor*boost, '--',
                    label=label)
            # ax.plot(t_array['up']*xfactor, (E_tot['up']+
            #         E_tot['down'])*yfactor, label=r'$E^{UP/DOWNsum}_{tot}$')

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            mpl.rcParams['axes.color_cycle'] = color_cycle

            # E_tot with components
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['sum']*yfactor, '--',
                    label=r'$E_{es}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['sum']*yfactor,
                    label=r'$E_{Total}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['sum']*yfactor, '--',
                    label=r'$E_{ind}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['sum']*yfactor, '--',
                    label=r'$E_{rad}$')

            # ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
            #         (run_data['%d' % run]['E_ind']['sum'] +
            #          run_data['%d' % run]['E_rad']['sum'])*yfactor*boost, '.',
            #          label=r'$E_{ind+rad} \times$ %d' % boost)

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels, loc=5)

            p = df.pickerPlot(fig, ax)
            p.plot()

            # E_tot with components and no label
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['sum']*yfactor, '--',
                    label=r'$E_{es}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_tot']['sum']*yfactor,
                    label=r'$E_{Total}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['sum']*yfactor, '--',
                    label=r'$E_{ind}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['sum']*yfactor, '--',
                    label=r'$E_{rad}$')

            # ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
            #         (run_data['%d' % run]['E_ind']['sum'] +
            #          run_data['%d' % run]['E_rad']['sum'])*yfactor*boost, '.',
            #          label=r'$E_{ind+rad} \times$ %d' % boost)

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'es' in components:
            mpl.rcParams['axes.color_cycle'] = color_cycle

            ### E_es
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['rs']*yfactor, '+',
                    label=r'$E^{RS}_{es}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['sum']*yfactor,
                    label=r'$E^{Total}_{es}$')

            if boost == 1.0:
                label = r'$E^{UP}_{es}$'
            else:
                label = r'$E^{UP}_{es} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['up']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['up']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{DOWN}_{es}$'
            else:
                label = r'$E^{DOWN}_{es} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['down']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['down']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{REF}_{es}$'
            else:
                label = r'$E^{REF}_{es} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor-xoffset,
                    run_data['%d' % run]['E_es']['ref']*yfactor*boost, '.',
                    label=label)

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            #ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels, loc=5)

        if 'ind' in components:
            mpl.rcParams['axes.color_cycle'] = color_cycle_alt

            ### E_ind
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['rs']*yfactor, '+',
                    label=r'$E^{RS}_{ind}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['sum']*yfactor,
                    label=r'$E^{Total}_{ind}$')

            if boost == 1.0:
                label = r'$E^{UP}_{ind}$'
            else:
                label = r'$E^{UP}_{ind} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['up']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['up']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{DOWN}_{ind}$'
            else:
                label = r'$E^{DOWN}_{ind} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['down']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['down']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{REF}_{ind}$'
            else:
                label = r'$E^{REF}_{ind} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor-xoffset,
                    run_data['%d' % run]['E_ind']['ref']*yfactor*boost, '.',
                    label=label)

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            #ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels)

        if 'rad' in components:
            mpl.rcParams['axes.color_cycle'] = color_cycle_alt

            ### E_rad
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(run_data['%d' % run]['t_array']['rs']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['rs']*yfactor, '+',
                    label=r'$E^{RS}_{rad}$')
            ax.plot(run_data['%d' % run]['t_array']['sum']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['sum']*yfactor,
                    label=r'$E^{Total}_{rad}$')

            if boost == 1.0:
                label = r'$E^{UP}_{rad}$'
            else:
                label = r'$E^{UP}_{rad} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['up']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['up']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{DOWN}_{rad}$'
            else:
                label = r'$E^{DOWN}_{rad} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['down']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['down']*yfactor*boost, '--',
                    label=label)

            if boost == 1.0:
                label = r'$E^{REF}_{rad}$'
            else:
                label = r'$E^{REF}_{rad} \times$ %d' % boost

            ax.plot(run_data['%d' % run]['t_array']['ref']*xfactor-xoffset,
                    run_data['%d' % run]['E_rad']['ref']*yfactor*boost, '.',
                    label=label)

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            #ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels)

def plot_runs_dE(runs, run_data, eventName, eventRS, dE_mult,
                 components=['tot', 'es', 'ind', 'rad'], boost=5.0,
                 xlim=[-2,15]):

    mpl.rcParams['axes.color_cycle'] = color_cycle

    xlabel = r'Time (microseconds)'
    xfactor = 1E6

    ylabel = 'd/dt E-field (kV/m/us)'
    yfactor = 1E-9

    # xlim = [-2,15]
    #~ ylim = [0, 15]

    xoffset = 5.0  # in usec

    for run in runs:
        sup_title = 'UF %s-%s (RS #%d) - %d m' % \
                    (eventName[:2], eventName[2:], eventRS,
                     run_data['%d' % run]['D']['rs'])

        # Only for comparing TL, MTLE, and MTLL. Comment out otherwise
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
        #

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(run_data['%d'%runs[0]]['t_array']['dE_measured'],
                    run_data['%d'%runs[0]]['E_tot']['dE_measured']*yfactor/dE_mult,
                    label=r'Measured $\div$ %0.02f' % dE_mult)

        dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
        dE_sum = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)

        ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                dE_sum*yfactor, '-',
                label='MTLE')

        ax.set_title(sup_title)
        # ax.set_xlabel(xlabel)
        # ax.set_ylabel(ylabel)
        ax.set_xlim(xlim)
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
        ax.grid(True,which='both')

        ax.legend()

        p = df.pickerPlot(fig, ax)
        p.plot()


        if 'tot' in components:

            # # Field with label
            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            #
            # dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            # dE_sum = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)
            # dE_rs = np.gradient(run_data['%d'%run]['E_tot']['rs'], dt)
            # dE_up = np.gradient(run_data['%d'%run]['E_tot']['up'], dt)
            # dE_down = np.gradient(run_data['%d'%run]['E_tot']['down'], dt)
            # dE_ref = np.gradient(run_data['%d'%run]['E_tot']['ref'], dt)
            #
            # ax.plot(run_data['%d'%run]['t_array']['rs']*xfactor-xoffset,
            #         dE_rs*yfactor*dE_mult, '+',
            #         label=r'$dE_{RS} \times$ %0.2f' % (dE_mult))
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_sum*yfactor*dE_mult, '-',
            #         label=r'$dE_{Total} \times$  %0.2f' % (dE_mult))
            #
            # ax.plot(run_data['%d'%run]['t_array']['up']*xfactor-xoffset,
            #         dE_up*yfactor*dE_mult*boost, '--',
            #         label=r'$dE_{UP} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.plot(run_data['%d'%run]['t_array']['down']*xfactor-xoffset,
            #         dE_down*yfactor*dE_mult*boost, '--',
            #         label=r'$dE_{DOWN} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.plot(run_data['%d'%run]['t_array']['ref']*xfactor-xoffset,
            #         dE_ref*yfactor*dE_mult*boost, '.',
            #         label=r'$dE_{REF} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.set_title(sup_title)
            # #ax.set_xlabel(xlabel)
            # #ax.set_ylabel(ylabel)
            # ax.set_xlim(xlim)
            # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.grid(True,which='both')
            #
            # ax.legend()
            #
            # p = df.pickerPlot(fig, ax)
            # p.plot()
            #
            # # Field without label for clean plot
            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            # ax.plot(run_data['%d'%runs[0]]['t_array']['dE_measured'],
            #         run_data['%d'%runs[0]]['E_tot']['dE_measured']*yfactor,
            #         label='Measured')
            #
            # dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            # dE_sum = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)
            # dE_rs = np.gradient(run_data['%d'%run]['E_tot']['rs'], dt)
            # dE_up = np.gradient(run_data['%d'%run]['E_tot']['up'], dt)
            # dE_down = np.gradient(run_data['%d'%run]['E_tot']['down'], dt)
            # dE_ref = np.gradient(run_data['%d'%run]['E_tot']['ref'], dt)
            #
            # ax.plot(run_data['%d'%run]['t_array']['rs']*xfactor-xoffset,
            #         dE_rs*yfactor*dE_mult, '+',
            #         label=r'$dE_{RS} \times$ %0.2f' % (dE_mult))
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_sum*yfactor*dE_mult, '-',
            #         label=r'$dE_{Total} \times$  %0.2f' % (dE_mult))
            #
            # ax.plot(run_data['%d'%run]['t_array']['up']*xfactor-xoffset,
            #         dE_up*yfactor*dE_mult*boost, '--',
            #         label=r'$dE_{UP} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.plot(run_data['%d'%run]['t_array']['down']*xfactor-xoffset,
            #         dE_down*yfactor*dE_mult*boost, '--',
            #         label=r'$dE_{DOWN} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.plot(run_data['%d'%run]['t_array']['ref']*xfactor-xoffset,
            #         dE_ref*yfactor*dE_mult*boost, '.',
            #         label=r'$dE_{REF} \times$  %0.2f' % (dE_mult*boost))
            #
            # ax.set_title(sup_title)
            # #ax.set_xlabel(xlabel)
            # #ax.set_ylabel(ylabel)
            # ax.set_xlim(xlim)
            # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.grid(True, which='both')
            #
            # p = df.pickerPlot(fig, ax)
            # p.plot()
            #
            # # Field with label and all components for total
            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            #
            # dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            # dE_tot = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)
            # dE_es = np.gradient(run_data['%d'%run]['E_es']['sum'], dt)
            # dE_ind = np.gradient(run_data['%d'%run]['E_ind']['sum'], dt)
            # dE_rad = np.gradient(run_data['%d'%run]['E_rad']['sum'], dt)
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_es*yfactor, '+', label=r'$dE_{es}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_tot*yfactor, '-', label=r'$dE_{Total}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_ind*yfactor, '--', label=r'$dE_{ind}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_rad*yfactor, '.', label=r'$dE_{rad}$')
            #
            # ax.set_title(sup_title)
            # #ax.set_xlabel(xlabel)
            # #ax.set_ylabel(ylabel)
            # ax.set_xlim(xlim)
            # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.grid(True,which='both')
            #
            # handles, labels = ax.get_legend_handles_labels()
            # handles[0], handles[1] = handles[1], handles[0]
            # labels[0], labels[1] = labels[1], labels[0]
            # ax.legend(handles, labels)
            #
            # p = df.pickerPlot(fig, ax)
            # p.plot()
            #
            # # Field without label and all components for total
            # fig = plt.figure()
            # ax = fig.add_subplot(111)
            #
            # dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            # dE_tot = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)
            # dE_es = np.gradient(run_data['%d'%run]['E_es']['sum'], dt)
            # dE_ind = np.gradient(run_data['%d'%run]['E_ind']['sum'], dt)
            # dE_rad = np.gradient(run_data['%d'%run]['E_rad']['sum'], dt)
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_es*yfactor, '+', label=r'$dE_{es}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_tot*yfactor, '-', label=r'$dE_{Total}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_ind*yfactor, '--', label=r'$dE_{ind}$')
            #
            # ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
            #         dE_rad*yfactor, '.', label=r'$dE_{rad}$')
            #
            # ax.set_title(sup_title)
            # #ax.set_xlabel(xlabel)
            # #ax.set_ylabel(ylabel)
            # ax.set_xlim(xlim)
            # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            # ax.grid(True,which='both')
            #
            # p = df.pickerPlot(fig, ax)
            # p.plot()

            # Total field only
            fig = plt.figure()
            ax = fig.add_subplot(111)
            yfactor = 1.0
            dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            dE_tot = np.gradient(run_data['%d'%run]['E_tot']['sum'], dt)

            if run_data['%d'%run]['D']['rs'] == 92:
                # print('%0.2e' % np.max(dE_tot[0:int(len(dE_tot)/4)]))
                yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
            if run_data['%d'%run]['D']['rs'] == 181:
                # print('%0.2e' % np.max(dE_tot[0:int(len(dE_tot)/4)]))
                yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
            if run_data['%d'%run]['D']['rs'] == 249:
                # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
            if run_data['%d'%run]['D']['rs'] == 326:
                # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
            if run_data['%d'%run]['D']['rs'] == 500:
                # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])

            ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                    dE_tot*yfactor, '-', label=r'$dE_{Total} (D = %d)$' %
                                               run_data['%d'%run]['D']['rs'])
            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.set_ylim([-0.25, 1.1])
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            ax.legend()

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'es' in components:
            # Field with label
            fig = plt.figure()
            ax = fig.add_subplot(111)

            dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            dE_sum = np.gradient(run_data['%d'%run]['E_es']['sum'], dt)
            dE_rs = np.gradient(run_data['%d'%run]['E_es']['rs'], dt)
            dE_up = np.gradient(run_data['%d'%run]['E_es']['up'], dt)
            dE_down = np.gradient(run_data['%d'%run]['E_es']['down'], dt)
            dE_ref = np.gradient(run_data['%d'%run]['E_es']['ref'], dt)

            ax.plot(run_data['%d'%run]['t_array']['rs']*xfactor-xoffset,
                    dE_rs*yfactor*dE_mult, '+',
                    label=r'$dE^{RS}_{es} \times$ %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                    dE_sum*yfactor*dE_mult, '-',
                    label=r'$dE^{Total}_{es} \times$  %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['up']*xfactor-xoffset,
                    dE_up*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{UP}_{es} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['down']*xfactor-xoffset,
                    dE_down*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{DOWN}_{es} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['ref']*xfactor-xoffset,
                    dE_ref*yfactor*dE_mult*boost, '.',
                    label=r'$dE^{REF}_{es} \times$  %0.2f' % (dE_mult*boost))

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'ind' in components:
            # Field with label
            fig = plt.figure()
            ax = fig.add_subplot(111)

            dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            dE_sum = np.gradient(run_data['%d'%run]['E_ind']['sum'], dt)
            dE_rs = np.gradient(run_data['%d'%run]['E_ind']['rs'], dt)
            dE_up = np.gradient(run_data['%d'%run]['E_ind']['up'], dt)
            dE_down = np.gradient(run_data['%d'%run]['E_ind']['down'], dt)
            dE_ref = np.gradient(run_data['%d'%run]['E_ind']['ref'], dt)

            ax.plot(run_data['%d'%run]['t_array']['rs']*xfactor-xoffset,
                    dE_rs*yfactor*dE_mult, '+',
                    label=r'$dE^{RS}_{ind} \times$ %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                    dE_sum*yfactor*dE_mult, '-',
                    label=r'$dE^{Total}_{ind} \times$  %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['up']*xfactor-xoffset,
                    dE_up*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{UP}_{ind} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['down']*xfactor-xoffset,
                    dE_down*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{DOWN}_{ind} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['ref']*xfactor-xoffset,
                    dE_ref*yfactor*dE_mult*boost, '.',
                    label=r'$dE^{REF}_{ind} \times$  %0.2f' % (dE_mult*boost))

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'rad' in components:
            # Field with label
            fig = plt.figure()
            ax = fig.add_subplot(111)

            dt = np.diff(run_data['%d'%run]['t_array']['sum'])[0]
            dE_sum = np.gradient(run_data['%d'%run]['E_rad']['sum'], dt)
            dE_rs = np.gradient(run_data['%d'%run]['E_rad']['rs'], dt)
            dE_up = np.gradient(run_data['%d'%run]['E_rad']['up'], dt)
            dE_down = np.gradient(run_data['%d'%run]['E_rad']['down'], dt)
            dE_ref = np.gradient(run_data['%d'%run]['E_rad']['ref'], dt)

            ax.plot(run_data['%d'%run]['t_array']['rs']*xfactor-xoffset,
                    dE_rs*yfactor*dE_mult, '+',
                    label=r'$dE^{RS}_{rad} \times$ %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['sum']*xfactor-xoffset,
                    dE_sum*yfactor*dE_mult, '-',
                    label=r'$dE^{Total}_{rad} \times$  %0.2f' % (dE_mult))

            ax.plot(run_data['%d'%run]['t_array']['up']*xfactor-xoffset,
                    dE_up*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{UP}_{rad} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['down']*xfactor-xoffset,
                    dE_down*yfactor*dE_mult*boost, '--',
                    label=r'$dE^{DOWN}_{rad} \times$  %0.2f' % (dE_mult*boost))

            ax.plot(run_data['%d'%run]['t_array']['ref']*xfactor-xoffset,
                    dE_ref*yfactor*dE_mult*boost, '.',
                    label=r'$dE^{REF}_{rad} \times$  %0.2f' % (dE_mult*boost))

            ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            handles, labels = ax.get_legend_handles_labels()
            handles[0], handles[1] = handles[1], handles[0]
            labels[0], labels[1] = labels[1], labels[0]
            ax.legend(handles, labels)

            p = df.pickerPlot(fig, ax)
            p.plot()

def plot_runs_dE_together(runs, run_data, waves, eventName, eventRS,
                          measured_mult, dE_mult,
                          components=['tot', 'es', 'ind', 'rad'],
                          xlim=[-2,15]):
    mpl.rcParams['axes.color_cycle'] = color_cycle

    xlabel = r'Time (microseconds)'
    xfactor = 1E6

    ylabel = 'E-field (kV/m)'
    yfactor = 1E-3

    # xlim = [-2,30]
    #~ ylim = [0, 15]

    xoffset = 5.0  # in usec

    sup_title = 'UF %s-%s (RS #%d)' % (eventName[:2], eventName[2:], eventRS)

    for wave in waves:

        if 'tot' in components:
            ### E_tot
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                yfactor = 1.0
                dt = np.diff(run_data['%d'%run]['t_array']['{0}'.format(wave)])[0]

                E_tot = run_data['%d'%run]['E_tot']['{0}'.format(wave)]
                dE_tot = np.gradient(E_tot, dt)

                label = r'$MTLE_{total}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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
                elif run == 27:
                    label = r'$\lambda =$ 3 km'
                elif run == 47:
                    label = r'$\lambda =$ 2 km'
                ###

                linestyle ='-'

                if run == 35 or run == 38:
                    linestyle = '-'

                if run_data['%d'%run]['D']['rs'] == 92:
                    # print('%0.2e' % np.max(dE_tot[0:int(len(dE_tot)/4)]))
                    yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
                if run_data['%d'%run]['D']['rs'] == 181:
                    # print('%0.2e' % np.max(dE_tot[0:int(len(dE_tot)/4)]))
                    yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
                if run_data['%d'%run]['D']['rs'] == 249:
                    # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                    yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
                    label = r'$dE_{Total} (D = 249)$'

                if run_data['%d'%run]['D']['rs'] == 326:
                    # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                    yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
                    label = r'$dE_{Total} (D = 326)$'

                if run_data['%d'%run]['D']['rs'] == 500:
                    # print('%0.2e' % np.max(dE_tot[0:len(dE_tot)/4]))
                    yfactor /= np.max(dE_tot[0:int(len(dE_tot)/4)])
                    label = r'$dE_{Total} (D = 500)$'

                # print('%0.2e' % yfactor)
                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, dE_tot*yfactor, linestyle, label=label)

            # ax.set_title(sup_title)
            # ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')

            fig2 = plt.figure()
            handles, labels = ax.get_legend_handles_labels()
            labels = [labels[-1], labels[1], labels[0]]
            handles = [handles[-1], handles[1], handles[0]]
            fig2.legend(handles, labels)

            # handles, labels = ax.get_legend_handles_labels()
            # h1 = handles.pop(1)
            # l1 = labels.pop(1)
            #
            # handles.append(h1)
            # labels.append(l1)
            # ax.legend(handles, labels, loc=4)
            # ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'es' in components:
            ### E_es
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                dt = np.diff(run_data['%d'%run]['t_array']['{0}'.format(wave)])[0]
                E_es = run_data['%d'%run]['E_es']['{0}'.format(wave)]
                dE_es = np.gradient(E_es, dt)

                label = r'$MTLE_{es}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, dE_es*yfactor, '-', label=label)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'ind' in components:
            ### E_ind
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                dt = np.diff(run_data['%d'%run]['t_array']['{0}'.format(wave)])[0]
                E_ind = run_data['%d'%run]['E_ind']['{0}'.format(wave)]
                dE_ind = np.gradient(E_ind, dt)

                label = r'$MTLE_{ind}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, dE_ind*yfactor, '-', label=label)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

        if 'rad' in components:
            ### E_rad
            fig = plt.figure()
            ax = fig.add_subplot(111)

            for run in runs:
                dt = np.diff(run_data['%d'%run]['t_array']['{0}'.format(wave)])[0]
                E_rad = run_data['%d'%run]['E_rad']['{0}'.format(wave)]
                dE_rad = np.gradient(E_rad, dt)

                label = r'$MTLE_{rad}^{%s}$ (D = %d)' % (wave, run_data['%d'%run]['D']['rs'])

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

                ax.plot(run_data['%d'%run]['t_array']['{0}'.format(wave)]*xfactor-xoffset, dE_rad*yfactor, '-', label=label)

            ax.set_title(sup_title)
            ax.set_xlabel(xlabel)
            # ax.set_ylabel(ylabel)
            ax.set_xlim(xlim)
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.grid(True,which='both')
            ax.legend(loc=4)

            p = df.pickerPlot(fig, ax)
            p.plot()

def get_run_data(runs, eventName, eventRS, measured_key, measured_dE_key):
    run_data = {}

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
        fileName = '/home/jaime/Documents/Python Code/Data Sets/DataFiles/Backup_11062015/UF0920_data_061809_rs3.p'

        data = pickle.load(open(fileName, 'rb'))

        E_tot['measured'] = data[measured_key]['data']
        t_array['measured'] = data['time']
        #~ D5 = data['D']
        i['measured'] = data['II_HI']['data']
        i_array['measured'] = data['II_HI']['data']
        t_array['dE_measured'] = data[measured_dE_key]['time']
        E_tot['dE_measured'] = data[measured_dE_key]['data']

        fileName = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/Models/MTLE/1 Reflection/ResultsGeneralTL/UF%sRS%d/Run%02d/data_sum.p' % (eventName, eventRS, run)

        data = pickle.load(open(fileName, 'rb'))

        E_es['sum'] = data['E_es']
        E_ind['sum'] = data['E_ind']
        E_rad['sum'] = data['E_rad']
        E_tot['sum'] = data['E']
        t_array['sum'] = data['time']
        D['sum'] = data['D']
        v['sum'] = data['v']
        #~ vr['sum'] = data['vr']
        #~ Ht['sum'] = data['Ht']
        #~ dz['sum'] = data['dz']
        #~ i['sum'] = data['i']
        i_array['sum'] = data['i_array']
        di_array['sum'] = data['di_array']
        z_array['sum'] = data['z_array']
        lmb['sum'] = data['lmb']

        # ### Add up all the waves
        # E_ess = E_es['rs'] + E_es['up'] + E_es['down'] + E_es['ref']
        # E_indd = E_ind['rs'] + E_ind['up'] + E_ind['down'] + E_ind['ref']
        # E_radd = E_rad['rs'] + E_rad['up'] + E_rad['down'] + E_rad['ref']
        # E_tott = E_tot['rs'] + E_tot['up'] + E_tot['down'] + E_tot['ref']
        # t_arrayy = t_array['rs']
        #
        # E_es['sum'] = E_ess
        # E_ind['sum'] = E_indd
        # E_rad['sum'] = E_radd
        # E_tot['sum'] = E_tott
        # t_array['sum'] = t_arrayy

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

    return run_data

def main():
    c = 3.0E8

    eventDate = '061809'
    eventName = '0920'
    eventRS = 3
    dist = 92.0
    # dist = 257.0
    dist = 326.0
    # dist = 500.0
    # dist = 316.0
    # dist = 181.0
    # dist = 42.0E3
    # dist = 249.0
    # dist = 444.0
    # dist = 1E6
    ttype = 'measured'

    runs = None
    # run_data = {}

    waves = ['sum','rs','down','up','ref']

    if dist == 92.0:
        measured_key = 'E_5'
        measured_dE_key = 'dE_5'
        dE_mult = 2.65
        measured_mult = 1.03
        # runs = [1, 2, 3, 4, 5, 6, 7, 8]
        # runs = [14, 7, 15]  # TL, MTLE, and MTLL
        # runs = [7, 15, 16, 17]
        # runs = [19]
        # runs = [29, 26, 27, 28, 19]
        runs = [27, 44] # Best simulation for this distance
        runs = [27, 19, 46] # Diff speed, constant speed
        runs = [27, 47]  # lmb = 3e3 vs 2e3

    elif dist == 1E6: # Used to plot all distances together
        measured_key = 'E_5'
        measured_dE_key = 'dE_5'
        dE_mult = 2.65
        measured_mult = 1.0
        runs = [27, 39, 36, 38, 35, 41, 40, 42] # Distances from 92 to 42000 m
        # runs = [27, 36, 38, 35, 40] # Distances 92, 181, 249, 326, and 500 m
        runs = [42]

    elif dist == 257.0:
        measured_key = 'E_23'
        measured_dE_key = 'dE_8'  # Not co-located
        dE_mult = 2.65  #4.0
        measured_mult = 1.0  #0.3
        runs = [9, 10]
        runs = [19, 24, 23, 20, 21, 22]
        runs = [20]

    elif dist == 326.0:
        measured_key = 'E_18'
        measured_dE_key = 'dE_11'  # Not co-located 316 m
        dE_mult = 2.65
        measured_mult = 0.85  # 0.77
        runs = [11]
        runs = [21]
        runs = [35, 45]
        runs = [40, 35, 38]

    elif dist == 316.0:
        measured_key = 'E_18'  # 326 m
        measured_dE_key = 'dE_11'
        dE_mult = 2.65
        measured_mult = 1.3  # Not correct
        runs = [12]
        runs = [25]
        runs = [37]
        runs = [37, 48]  # lmb = 3e3 vs 2e3

    elif dist == 181.0:
        measured_key = 'E_18' # Not co-located
        measured_dE_key = 'dE_8'
        dE_mult = 2.65
        measured_mult = 1.0 # Not correct
        runs = [13]
        runs = [23]
        runs = [36]

    elif dist == 500:
        measured_key = 'E_18'
        measured_dE_key = 'dE_11' # Not co-located
        dE_mult = 2.65
        measured_mult = 1.0
        runs = [40]

    elif dist == 42.0E3:
        measured_key = 'E_LOG'
        measured_dE_key = 'E_18'#'dE_LOG'
        dE_mult = 2.65
        measured_mult = 1.0
        runs = [42]

    elif dist == 249:
        measured_key = 'E_23'  # 257 m
        measured_dE_key = 'dE_4'
        dE_mult = 2.65
        measured_mult = 0.4
        runs = [38]

    elif dist == 444:
        measured_key = 'E_9'  # 443m
        measured_dE_key = 'dE_9'
        dE_mult = 2.65
        measured_mult = 1.0
        runs = [41]

    # Get data from runs
    run_data = get_run_data(runs, eventName, eventRS, measured_key,
                            measured_dE_key)


    # print(run_data['27']['i_array']['down'].shape)
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.plot(run_data['27']['t_array']['down']*1e6, run_data['27']['i_array']['down'][:, 0]*1e-3)
    # ax.set_xlim([0, 30])
    # ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    # ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
    # ax.grid(True,which='both')
    #
    # plt.show()
    # sys.exit(1)


    # Plot
    waves = ['sum']

    # plot_runs_together(runs, run_data, waves, eventName, eventRS,
    #                    measured_mult, components=['tot'], xlim=[-2,100])

    # plot_runs_individually(runs, run_data, eventName, eventRS, measured_mult,
    #                        components=['tot'], boost=5.0)

    # plot_runs_with_measured(runs, run_data, eventName, eventRS, measured_mult)

    # plot_runs_dE(runs, run_data, eventName, eventRS, dE_mult,
    #              components=['tot'], boost=5.0)

    plot_runs_dE_together(runs, run_data, waves, eventName, eventRS,
                          measured_mult, dE_mult, components=['tot'], xlim=[-1,16])

    plt.show()

if __name__ == "__main__":
    main()
