#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import scipy.integrate as integrate

import sys
import pickle
import operator

import xml.etree.ElementTree as et

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.lecroy as lc
import iclrt_tools.oscilloscopes.yoko850 as yk850

class DataSet(object):

    def __init__(self, xml_file):
        self.xml_file = xml_file

        # Get information from XML file
        self.root = et.parse(self.xml_file)

        day = self.root.find('date').find('day').text
        month = self.root.find('date').find('month').text
        year = self.root.find('date').find('year').text[-2:]

        self.eventDate = '%s%s%s' % (month, day, year)
        self.eventName = self.root.find('name').text
        self.eventNamef = "%s%s%s" % (self.eventName[0:2],
                                      self.eventName[3:5], self.eventName[6:])

    def get_data_set(self, rs='all', meass='all'):
        mpl.rcParams['figure.dpi'] = 150

        data = {}
        self.rt_plots = {}
        wantOffset = True

        """
        Get data for each scope
        """
        print("Event: %s" % self.eventName)
        print("Date : %s" % self.eventDate)

        for rss in self.root.iter('return_stroke'):
            r_s = int(rss.find('number').text)

            if 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            print("\nRS   : #%d" % r_s)

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate, r_s)

            self.saved_keys = []
            self.fo = None

            if not("all" in meass.lower()):
                try:
                    self.fo = pickle.load(open(fileSave, "rb"))
                    self.saved_keys = self.fo.keys()

                except FileNotFoundError:
                    pass

            for scope in rss.iter('scope'):
                scope_data = {}
                scope_plots = {}

                # name = scope.find('name').text
                brand = scope.find('type').text
                path = scope.find('path').text

                for measurement in scope.iter('measurement'):
                    meas = {}

                    if self.saved_keys:
                        if "all" in meass.lower():
                            pass
                        elif meass in measurement.find('name').text:
                            pass
                        else:
                            continue
                        # elif measurement.find('name').text in saved_keys:
                            # continue

                    meas['name'] = measurement.find('name').text
                    meas['file'] = measurement.find('file').text
                    meas['trace'] = int(measurement.find('trace').text)
                    meas['cal_factor'] = float(measurement.find('cal_factor').text)
                    meas['units'] = measurement.find('units').text
                    meas['distance'] = float(measurement.find('distance').text)
                    meas['t_start'] = float(measurement.find('t_start').text)
                    meas['t_end'] = float(measurement.find('t_end').text)

                    scope_data[meas['name']] = meas

                """
                Read data files
                """
                for key in scope_data:
                    if "yoko" in brand.lower():
                        result = self.read_yoko(path, scope_data[key],
                                           scope_data[key]['t_start'],
                                           scope_data[key]['t_end'],
                                           wantOffset)

                    elif "lecroy" in brand.lower():
                        result = self.read_lecroy(path, scope_data[key])

                    scope_data[key]['result'] = result

                for key in scope_data:
                    """
                    Integrate the E-field derivatives (if any)
                    """
                    #~ ii_final = scope_data[key]['result'].data[:]
                    if ("int" in key.lower()):
                        # dt = np.diff(scope_data[key]['result'].dataTime)[0]
                        ind = 0 #len(scope_data[key]['result'].dataTime)/2.0 - 100E-6/dt

                        scope_data[key]['result'].data = integrate.cumtrapz(y=scope_data[key]['result'].data[ind:], x=scope_data[key]['result'].dataTime[ind:], initial=0)

                        scope_data[key]['result'].dataTime = scope_data[key]['result'].dataTime[ind:]

                    """
                    Smooth out the LOG waveforms
                    """

                    if ("log" in key.lower() or "golf" in key.lower()):
                        #~ from scipy.signal import savgol_filter
                        #~ savgol = savgol_filter(scope_data[key]['result'].data, 9, 5)
                        #~ print(xml_file)
                        window_length = 5.0
                        weights = np.repeat(1.0, window_length)/window_length
                        savgol = np.convolve(scope_data[key]['result'].data, weights, 'valid')

                        plt.plot(scope_data[key]['result'].data)
                        plt.plot(savgol)
                        plt.show()

                        scope_data[key]['result'].data = savgol

                        #~ sys.exit(1)

                    """
                    Get time intervals
                    """
                    print("Acquiring %s" % key)
                    scope_plots[key] = df.RelativeTimePlot(scope_data[key]['result'].dataTime[:len(scope_data[key]['result'].data)], scope_data[key]['result'].data, max_points=1E9)
                    scope_plots[key].plot()
                    #~ plt.plot(scope_data[key]['result'].dataTime, ii_final, '--')
                    plt.show()

                data.update(scope_data)
                self.rt_plots.update(scope_plots)

            #~ print(data.keys())
            #~ print(rt_plots.keys())
            #~
            #~ sys.exit(1)

            """
            Plot
            """
            if self.rt_plots:
                self.axes = {}
                lims = [5E-6, 195E-6]    # For data sets (200 us)
                # lims = [5E-6,45E-3]    # For Fourier analysis


                for key in self.rt_plots:
                    if("noise" in key.lower()):
                        fig, ax = self.rt_plots[key].relative_plot(1E6, [0, len(self.rt_plots[key].y)*self.rt_plots[key].delta_t])
                    else:
                        fig, ax = self.rt_plots[key].relative_plot(1E6, lims)

                    if "int" in key.lower():
                        ax.set_title('%s (D = %sm)' % ('Integrated d%s' % key[3:], data[key]['distance']))
                    else:
                        ax.set_title('%s (D = %sm)' % (key, data[key]['distance']))

                    ax.set_ylabel('(%s)' % data[key]['units'])

                    self.axes[key] = ax
                    #~ plt.show()
                    plt.close(fig)

        self.save_data(fileSave)

    def plot_data_set(self, rs='all', meass='all', lim=20, window=1.0,
                      norm=False):
        #~ mpl.rcdefaults()

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)

            data = pickle.load(open(fileSave, "rb"))

            event = '%s (RS #%d)' % (self.eventName, r_s)

            data_only = {}

            if "all" in meass:
                ignore = ['time', 'axes']

                dE = ['dE_1', 'dE_3', 'dE_4', 'dE_5', 'dE_7', 'dE_8', 'dE_9', 'dE_11', 'dE_25', 'dE_OB']
                intt = ['intE_1', 'intE_3', 'intE_4', 'intE_5', 'intE_7', 'intE_8', 'intE_9', 'intE_11', 'intE_25', 'intE_OB']

                # ignore.extend(['II_HI'])
                # ignore.extend(dE)
                ignore.extend(intt)

                for key in data:
                    if key in ignore:
                        pass
                    else:
                        data_only[key] = data[key]

                keys = data_only.keys()
                sort_data = {}

                for i, key in enumerate(keys):
                    value = data['axes'][key].get_title().split()

                    if len(value) == 4:
                        s = value[3]
                        ind = s.find('km')

                        if ind > 0:
                            temp = float(value[3][:ind])
                            s = '%d' % (temp*1E3)

                        ind = s.find('m')

                        if ind > 0:
                            s = value[3][:ind]

                        sort_data[key] = float(s)

                    else:
                        s = value[4]
                        ind = s.find('km')

                        if ind > 0:
                            temp = float(value[4][:ind])
                            s = '%d' % (temp*1E3)

                        ind = s.find('m')

                        if ind > 0:
                            s = value[4][:ind]

                        sort_data[key] = float(s)

                # sorted_data is an list of tuples of the form
                # (key, value)
                sorted_data = sorted(sort_data.items(),
                                     key=operator.itemgetter(1))

                """
                Print all in individual figures
                """
                #~ mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/LaTex/Pictures/Temp/E'

                mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/LaTex/Pictures/Temp/DataSets'

                for i in range(len(sorted_data)):

                    fig, ax = plt.subplots(1, 1)

                    #~ fig.suptitle('%s (%s/%s/%s)' % (event, eventDate[:2],eventDate[2:4], eventDate[4:]), fontsize=16)
                    #~ fig.suptitle(event)#, fontsize=16)

                    temp_data = data[sorted_data[i][0]]['data'][::int(len(data[sorted_data[i][0]]['data'])/len(data['time']))]

                    # print(sorted_data[i], len(data[sorted_data[i][0]]), len(temp_data), len(data['time']), np.max(temp_data))

                    zoom_lim = [-1, int(lim)]

                    # print(zoom_lim)

                    factor = 1E-3
                    l_width = 2.5

                    if 'dE_' in sorted_data[i][0]:
                        factor = 1E-9
                        l_width = 1.5

                    ax.plot(data['time'],factor*temp_data[0:len(data['time'])], linewidth=l_width)
                    ax.set_title(data['axes'][sorted_data[i][0]].get_title())

                    if "ii_hi" in sorted_data[i][0].lower():
                        ylabel = '(kA)'

                    elif "int" in sorted_data[i][0].lower():
                        ylabel = '(kV/m)'

                    elif "de" in sorted_data[i][0].lower():
                        ylabel = '(kV/m/$\mu$s)'

                    elif "e_" in sorted_data[i][0].lower():
                        ylabel = '(kV/m)'

                    else:
                        ylabel = data['axes'][sorted_data[i][0]].get_ylabel()

                    if '/us' in ylabel:
                        ylabel = ylabel[:-3] + ylabel[-1]

                    #~ ax.set_ylabel(ylabel)
                    ax.set_xlim(zoom_lim)
                    ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
                    ax.grid(True, which='both')
                    ax.xaxis.set_tick_params(width=1.5)
                    #~ ax.autoscale(True,'y')
                    #~ ax.set_xlabel('Time ($\mu$s)')

                    p = df.pickerPlot(fig, ax)
                    p.plot()

            else:
                mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/LaTex/Pictures/'

                x = data[meass]['time']
                y = data[meass]['data']

                y_filtered = self.moving_average(y, window)

                #~ plt.plot(x, y, '-', x,y_filtered, '--')

                norm_factor = 1.0
                factor = 1E-3
                l_width = 2.5

                if 'dE_' in meass:
                    factor = 1E-9
                    l_width = 1.5

                ### Normalize waveform
                if norm:
                    p = df.RelativeTimePlot(x,y)
                    p.plot()

                    plt.show()

                    zero = y[p.zero_ind]

                    p = df.RelativeTimePlot(x,y)
                    p.plot()

                    plt.show()

                    peak = y[p.zero_ind]

                    norm_factor = float(peak - zero)*factor

                fig = plt.figure()
                ax = fig.add_subplot(111)

                zoom_lim = [-1, int(lim)]

                # title = '%s (RS #%d)' % (self.eventName, r_s)
                # title = '%s (RS #%d)' % (self.eventName, r_s+1)
                # title = '%s (RS #1)' % (self.eventName)
                # title = '%s (ICC)' % self.eventName

                title = data['axes'][meass].get_title()
                distance = int(title.split('=')[1].strip().split('.')[0])
                title = '{0} (D = {1} m)'.format(meass, distance)

                # title = '{0} (RS #{1}) - {2} m'.format(self.eventName, rs, distance -1)

                if factor == 1E-3:
                    ylabel = '(k%s' % (data['axes'][meass].get_ylabel()[1:])
                else:
                    ylabel = data['axes'][meass].get_ylabel()

                xlabel = 'Time ($\mu$s)'

                ax.plot(x, y_filtered*factor/norm_factor, linewidth=l_width)
                # ax.set_title(title)
                #~ ax.set_ylabel(ylabel)
                #~ ax.set_xlabel(xlabel)
                ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
                ax.grid(True, which='both')
                ax.xaxis.set_tick_params(width=1.5)
                #~ ax.autoscale(True,'y')
                ax.set_xlim(zoom_lim)
                # ax.set_ylim([-1, 16])
                #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())

                p = df.pickerPlot(fig, ax)
                p.plot()

            plt.show()

    def save_data(self, fileSave):
        """
        Save data
        """
        if self.axes:

            if self.fo:
                file_data = self.fo
            else:
                file_data = {'axes': self.axes}

            for key in self.axes:
                file_data['axes'][key] = self.axes[key]
                file_data[key] = {}

                if 'log' in key.lower() or 'golf' in key.lower():

                    file_data[key]['data'] = self.axes[key].get_lines()[0].get_ydata() - self.rt_plots[key].y[(self.rt_plots[key].zero_time - self.rt_plots[key].x[0])/self.rt_plots[key].delta_t]

                    file_data[key]['time'] = self.axes[key].get_lines()[0].get_xdata()

                else:
                    #~ print("Offsetting %s by %0.2f" % (key, rt_plots[key].y[rt_plots[key].zero_ind]))

                    file_data[key]['data'] = self.axes[key].get_lines()[0].get_ydata() - self.rt_plots[key].y[self.rt_plots[key].zero_ind]

                    file_data[key]['time'] = self.axes[key].get_lines()[0].get_xdata()

            if not("time" in self.saved_keys):
                """
                Always save the time with the larger time step (fewer samples)
                to avoid problems when plotting them all together. The ones
                with a smaller time step (more samples) will be downsampled
                when plotted.
                """
                temp = {}

                for key in file_data:
                    if key != 'axes':
                        temp[key] = len(file_data[key]['data'])

                sort = sorted(temp.items(), key=operator.itemgetter(1))

                file_data['time'] = file_data[sort[0][0]]['time']#axes[sort[0][0]].get_lines()[0].get_xdata()

            pickle.dump(file_data, open(fileSave, "wb"))

            #~ try:
                #~ fo = pickle.load(open(fileSave, "rb"))
                #~ temp = {}
                #~
                #~ for key in fo:
                    #~ temp[key] = fo[key]
                    #~
                #~ for key in axes:
                    #~ temp[key] = file_data[key]
                    #~ temp['axes'][key] = axes[key]
                    #~
                #~ pickle.dump(temp, open(fileSave, "wb"))
                    #~
            #~ except FileNotFoundError:
                #~ pickle.dump(file_data, open(fileSave, "wb"))

    def moving_average(self, y, n=5):
        weights = np.repeat(1.0, n)/n
        sma = np.convolve(y, weights, 'same')
        return sma

    def read_yoko(self, path, scope_data, t_start, t_end, wantOffset):
        f = yk850.Yoko850File("%s/%s" % (path, scope_data['file']))
        header = f.get_header()

        try:
            return f.get_trace_data(header, scope_data['trace'], t_start,\
                            t_end, scope_data['cal_factor'], wantOffset)
        except AttributeError:
            print("\n\nERROR: Invalid file.")
            sys.exit(1)

    def read_lecroy(self, path, scope_data):
        lecroy = lc.lecroy_data("%s/%s" % (path, scope_data['file']))
        lecroy.get_seg_time()
        lecroy.get_segment(scope_data['trace'], scope_data['cal_factor'])
        offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
        lecroy.data -= offset

        return lecroy

    def print_keys(self, rs='all'):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate, r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS #%d:' % (self.eventName, r_s)

            keys = data.keys()

            print(event)
            ignore = ['time', 'axes']

            for key in keys:
                if not(key in ignore):
                    print('    ' + key)
            print()

    def calc_rise(self, rs='all', meass='all'):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass]['data']
                time = data[meass]['time']*1.0E-6

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Get Noise Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()

                mean = np.mean(y)
                std = np.std(y)
                three_sigma = 3*std

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii - mean)
                plt.title('Select rise only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                # y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                peak = np.max(y)
                amp = peak - three_sigma

                t_start = np.argmax(np.abs(1.0/(0.1*amp + three_sigma - y)))
                t_end = np.argmax(np.abs(1.0/(0.9*amp + three_sigma - y)))

                rise_time = (t[t_end] - t[t_start])*1.0E9

                tt_start = np.argmax(np.abs(1.0/(three_sigma - y)))

                ind1 = np.where(time == t[tt_start])
                ind2 = np.where(time == t[t_start])
                ind3 = np.where(time == t[t_end])

                time *= 1.0E9

                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(time, ii - mean, '-x')
                ax.plot(time[ind2],ii[ind2], 'ro')
                ax.plot(time[ind3], ii[ind3], 'ro')
                ax.set_title('Peak and Risetime')

                ylims = plt.gca().get_ylim()
                ax.plot([time[ind1], time[ind1]], [ylims[0], ylims[1]],
                         '--r', linewidth=1.0)
                ax.plot([time[ind2], time[ind2]], [ylims[0], ylims[1]],
                         '--r', linewidth=1.0)
                ax.plot([time[ind3], time[ind3]], [ylims[0], ylims[1]],
                         '--r', linewidth=1.0)

                xlims = plt.gca().get_xlim()
                ax.plot([xlims[0],xlims[1]], [ii[ind2],ii[ind2]],
                         '--r', linewidth=1.0)
                ax.plot([xlims[0],xlims[1]], [ii[ind3],ii[ind3]],
                         '--r', linewidth=1.0)

                ax.plot([xlims[0],xlims[1]], [0,0],
                         '--k', linewidth=1.0)
                ax.plot([xlims[0],xlims[1]], [three_sigma,three_sigma],
                         '--g', linewidth=1.0)

                plt.text((xlims[-1] - xlims[0])/2 + xlims[0],(ylims[-1] - ylims[0])/2 + ylims[0]+1000, 'Peak = %0.2f kA' % ((peak)*1.0E-3))
                plt.text((xlims[-1] - xlims[0])/2 + xlims[0],(ylims[-1] - ylims[0])/2 + ylims[0], 'Risetime = %0.2f ns' % rise_time)

                ax.set_xlim([0,30E-6*1E9])

                print('RS # %d => %s: %0.2f A %0.2f ns' % (r_s, meass, peak,
                                                            rise_time))

                p = df.plotdf(fig, ax)
                p.plot()

                plt.show()

    def calc_dip_time(self, rs='all', meass='all', window=1.0):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass]['data']
                ii = self.moving_average(ii, window)
                time = data[meass]['time']*1.0E-6

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Get Noise Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()

                mean = np.mean(y)
                std = np.std(y)
                three_sigma = mean + 2*std

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Get Rise Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                peak = np.max(y)
                amp = peak - three_sigma

                ind_ten = np.argmax(np.abs(1.0/(0.1*amp + three_sigma - y)))
                ind_ninety = np.argmax(np.abs(1.0/(0.9*amp + three_sigma - y)))

                ind_start = np.argmax(np.abs(1.0/(three_sigma - y)))
                t_start = t[ind_start]
                t_max = t[np.argmax(y)]

                t_ten = t[ind_ten]
                t_ninety = t[ind_ninety]

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Get Dip Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                amp = np.max(y) - np.min(y)
                dip_peak = amp

                ind_end = 0
                t_end = t[ind_end]
                t_min = t[np.argmin(y)]

                ind1 = np.where(time == t_start)
                ind2 = np.where(time == t_end)
                ind3 = np.where(time == t_max)
                ind4 = np.where(time == t_min)

                risetime = t_ninety - t_ten

                delay = t_end - t_start
                delay1 = t_min - t_max

                plt.plot(time*1E6, ii - mean)
                ylims = plt.gca().get_ylim()
                plt.plot([time[ind1]*1E6, time[ind1]*1E6],
                         [ylims[0], ylims[1]],'r')
                plt.plot([time[ind2]*1E6, time[ind2]*1E6],
                         [ylims[0], ylims[1]], 'r')
                plt.plot([time[ind3]*1E6, time[ind3]*1E6],
                         [ylims[0], ylims[1]], 'g')
                plt.plot([time[ind4]*1E6, time[ind4]*1E6],
                         [ylims[0], ylims[1]], 'g')

                xlims = plt.gca().get_xlim()
                plt.plot([xlims[0],xlims[1]], [0,0],
                         '--k', linewidth=1.0)
                plt.plot([xlims[0],xlims[1]],
                         [three_sigma - mean, three_sigma - mean],
                         '--g', linewidth=1.0)

                plt.text(time[ind1]*1E6,0, '%0.2f (us)' % (delay*1E6), color='red')
                plt.text(time[ind4]*1E6,0, '%0.2f (us)' % (delay1*1E6), color='green')
                plt.xlim([0,30])


                print('RS # %d => Peak: %0.2f (kA)' % (r_s, peak*1E-3))
                print('RS # %d => Risetime: %0.2f (ns)' %
                      (r_s, risetime*1.0E9))
                print('RS # %d => Dip Peak: %0.2f (kA)' %
                      (r_s, dip_peak*1E-3))
                print('RS # %d => Dip Delay start to start: %0.2f (us)' %
                      (r_s, delay*1E6))
                print('RS # %d => Dip Delay peak to dip: %0.2f (us)' %
                      (r_s, delay1*1E6))
                plt.show()

    def calc_dip_time_e(self, rs='all', meass='all', window=1.0):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass]['data']
                time = data[meass]['time']*1.0E-6

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Get Rise Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                # y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                peak = np.max(y)
                # amp = peak - three_sigma

                # ind_ten = np.argmax(np.abs(1.0/(0.1*amp + three_sigma - y)))
                # ind_ninety = np.argmax(np.abs(1.0/(0.9*amp + three_sigma - y)))

                ind_start = 0  # np.argmax(np.abs(1.0/(three_sigma - y)))
                t_start = t[ind_start]
                t_max = t[np.argmax(y)]

                # t_ten = t[ind_ten]
                # t_ninety = t[ind_ninety]

                fig, ax = plt.subplots(1, 1)
                ax.plot(time, ii)
                plt.title('Get Dip Only')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                # y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                amp = np.max(y) - np.min(y)
                dip_peak = amp

                ind_end = 0
                t_end = t[ind_end]
                t_min = t[np.argmin(y)]

                ind1 = np.where(time == t_start)
                ind2 = np.where(time == t_end)
                ind3 = np.where(time == t_max)
                ind4 = np.where(time == t_min)

                # risetime = t_ninety - t_ten

                delay = t_end - t_start
                delay1 = t_min - t_max

                plt.plot(time*1E6, ii - mean)
                ylims = plt.gca().get_ylim()
                plt.plot([time[ind1]*1E6, time[ind1]*1E6],
                         [ylims[0], ylims[1]],'r')
                plt.plot([time[ind2]*1E6, time[ind2]*1E6],
                         [ylims[0], ylims[1]], 'r')
                plt.plot([time[ind3]*1E6, time[ind3]*1E6],
                         [ylims[0], ylims[1]], 'g')
                plt.plot([time[ind4]*1E6, time[ind4]*1E6],
                         [ylims[0], ylims[1]], 'g')

                xlims = plt.gca().get_xlim()
                plt.plot([xlims[0],xlims[1]], [0,0],
                         '--k', linewidth=1.0)
                # plt.plot([xlims[0],xlims[1]],
                #          [three_sigma - mean, three_sigma - mean],
                #          '--g', linewidth=1.0)

                plt.text(time[ind1]*1E6,0, '%0.2f (us)' % (delay*1E6), color='red')
                plt.text(time[ind4]*1E6,0, '%0.2f (us)' % (delay1*1E6), color='green')
                plt.xlim([0,30])


                print('RS # %d => Peak: %0.2f (kA)' % (r_s, peak*1E-3))
                print('RS # %d => Risetime: %0.2f (ns)' %
                      (r_s, risetime*1.0E9))
                print('RS # %d => Dip Peak: %0.2f (kA)' %
                      (r_s, dip_peak*1E-3))
                print('RS # %d => Dip Delay start to start: %0.2f (us)' %
                      (r_s, delay*1E6))
                print('RS # %d => Dip Delay peak to dip: %0.2f (us)' %
                      (r_s, delay1*1E6))
                plt.show()

    def calc_dip(self,rs='all', meass='all', window=1.0):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate, r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = self.moving_average(data[meass]['data'], window)
                time = data[meass]['time']*1.0E-6

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Calculate Dip')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                #~ y -= np.average(y[:20])

                time = p.ax.get_lines()[0].get_xdata()

                t_max = np.argmax(y)
                t_min = np.argmin(y)

                amp = np.max(y) - np.min(y)

                time *= 1E9

                plt.plot(time,y, '-x')
                plt.plot(time[t_max], y[t_max], 'ro')
                plt.plot(time[t_min], y[t_min], 'ro')
                plt.title('Dip')

                ylims = plt.gca().get_ylim()
                plt.plot([time[t_max], time[t_max]], [ylims[0], ylims[1]], 'r')
                plt.plot([time[t_min], time[t_min]], [ylims[0], ylims[1]], 'r')

                xlims = plt.gca().get_xlim()
                plt.plot([xlims[0],xlims[1]], [y[t_max],y[t_max]], 'r')
                plt.plot([xlims[0],xlims[1]], [y[t_min],y[t_min]], 'r')
                plt.text((xlims[-1] - xlims[0])/2 + xlims[0],(ylims[-1] - ylims[0])/2 + ylims[0], 'Peak = %0.2f kA' % (amp*1.0E-3))

                plt.show()

                print('RS # %d => %s: %0.2f kA' % (r_s, meass, amp*1E-3))

    def calc_dE_pulse(self, rs='all', meass='all'):

        for rss in self.root.iter('return_stroke'):

            r_s = int(rss.find('number').text)

            if rs == -1:
                pass
            elif 'all' in rs.lower():
                pass
            elif r_s == int(rs):
                pass
            else:
                continue

            fileSave = "./DataFiles/%s_data_%s_rs%d.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass]['data']
                time = data[meass]['time']*1.0E-6

                fig, ax = plt.subplots(1,1)
                ax.plot(time, ii)
                plt.title('Select RS peak and bipolar pulse')

                p = df.plotdf(fig, ax)
                p.plot()
                plt.show()

                y = p.ax.get_lines()[0].get_ydata()
                # y -= mean

                t = p.ax.get_lines()[0].get_xdata()

                peak = np.argmax(y)
                trough = np.argmin(y)

                delay = (t[trough] - t[peak])*1.0E9

                ind2 = np.where(time == t[peak])
                ind3 = np.where(time == t[trough])

                time *= 1.0E9

                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(time, ii, '-x')
                ax.plot(time[ind2],ii[ind2], 'ro')
                ax.plot(time[ind3], ii[ind3], 'ro')
                ax.set_title('dE/dt pulse delay')

                ylims = plt.gca().get_ylim()
                ax.plot([time[ind2], time[ind2]], [ylims[0], ylims[1]],
                         '--r', linewidth=1.0)
                ax.plot([time[ind3], time[ind3]], [ylims[0], ylims[1]],
                         '--r', linewidth=1.0)

                xlims = plt.gca().get_xlim()
                ax.plot([xlims[0],xlims[1]], [ii[ind2],ii[ind2]],
                         '--r', linewidth=1.0)
                ax.plot([xlims[0],xlims[1]], [ii[ind3],ii[ind3]],
                         '--r', linewidth=1.0)

                plt.text((xlims[-1] - xlims[0])/2 + xlims[0],(ylims[-1] - ylims[0])/2 + ylims[0], 'Risetime = %0.2f ns' % delay)

                ax.set_xlim([0,30E-6*1E9])

                print('RS # %d => %s: %0.2f ns' % (r_s, meass, delay))

                p = df.plotdf(fig, ax)
                p.plot()

                plt.show()
