#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import custom modules
import iclrt_tools.plotting.dfplots as df
import iclrt_tools.data_sets.waveforms as wvf
import iclrt_tools.filters.filters as filters

# Import other modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import pickle
import operator

import xml.etree.ElementTree as et


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
                                      self.eventName[3:5],
                                      self.eventName[6:])

    def get_data_set(self, rs='all', meass='all'):
        mpl.rcParams['figure.dpi'] = 150

        self.data = {}
        # self.rt_plots = {}

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
                                                             self.eventDate,
                                                             r_s)

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

                scope_name = scope.find('name').text
                scope_type = scope.find('type').text
                scope_path = scope.find('path').text

                for measurement in scope.iter('measurement'):
                    if self.saved_keys:
                        if "all" in meass.lower():
                            pass
                        elif meass in measurement.find('name').text:
                            pass
                        else:
                            continue

                    measurement_name = measurement.find('name').text
                    file_name = '{path}/{file}'.format(path=scope_path,
                                file=measurement.find('file').text)
                    trace = int(measurement.find('trace').text)
                    cal_factor = float(measurement.find('cal_factor').text)
                    units = measurement.find('units').text
                    distance = float(measurement.find('distance').text)
                    t_start = float(measurement.find('t_start').text)
                    t_end = float(measurement.find('t_end').text)

                    meas = wvf.Waveform(flash_name=self.eventName,
                                        event_date=self.eventDate,
                                        return_stroke=r_s,
                                        measurement_name=measurement_name,
                                        scope_name=scope_name,
                                        scope_type=scope_type,
                                        file_name=file_name,
                                        trace_number=trace,
                                        cal_factor=cal_factor,
                                        units=units, distance=distance,
                                        t_start=t_start, t_end=t_end)

                    scope_data[measurement_name] = meas

                self.data.update(scope_data)

        for key in self.data:
            print("Acquiring {meas}...".format(meas=key))
            self.data[key].get_data()

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

            data_only = {}

            if "all" in meass:
                ignore = []
                E = ['E_5', 'E_18', 'E_23', 'E_12F', 'E_12', 'E_NW60',
                     'E_NW100']
                dE = ['dE_1', 'dE_3', 'dE_4', 'dE_5', 'dE_7', 'dE_8', 'dE_9', 'dE_11', 'dE_17', 'dE_25', 'dE_OB']
                intt = ['intE_1', 'intE_3', 'intE_4', 'intE_5', 'intE_7', 'intE_8', 'intE_9', 'intE_11', 'intE_17', 'intE_25', 'intE_OB']

                ignore.extend(intt)
                ignore.extend(E)
                ignore.extend(['II_HI'])
                # ignore.extend(dE)

                for key in data:
                    if key in ignore:
                        pass
                    else:
                        data_only[key] = data[key]

                keys = data_only.keys()
                sort_data = {}

                for i, key in enumerate(keys):
                    value = data[key].ax.get_title().split()

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

                sorted_data = sorted(sort_data.items(),
                                     key=operator.itemgetter(1))

                """
                Print all in individual figures
                """
                mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/LaTex/Pictures/Temp/'

                for i in range(len(sorted_data)):

                    fig, ax = plt.subplots(1, 1)

                    #~ fig.suptitle('%s (%s/%s/%s)' % (event, eventDate[:2],eventDate[2:4], eventDate[4:]), fontsize=16)
                    #~ fig.suptitle(event)#, fontsize=16)

                    temp_data = data[sorted_data[i][0]].data

                    # print(sorted_data[i], len(data[sorted_data[i][0]]), len(temp_data), len(data['time']), np.max(temp_data))

                    zoom_lim = [-1, int(lim)]

                    # print(zoom_lim)

                    factor = 1E-3
                    l_width = 2.5

                    if 'dE_' in sorted_data[i][0]:
                        factor = 1E-9
                        l_width = 1.5

                    ax.plot(data[sorted_data[i][0]].dataTime, factor*temp_data,
                            linewidth=l_width)
                    ax.set_title(data[sorted_data[i][0]].ax.get_title())

                    if "ii_hi" in sorted_data[i][0].lower():
                        ylabel = '(kA)'

                    elif "int" in sorted_data[i][0].lower():
                        ylabel = '(kV/m)'

                    elif "de" in sorted_data[i][0].lower():
                        ylabel = '(kV/m/$\mu$s)'

                    elif "e_" in sorted_data[i][0].lower():
                        ylabel = '(kV/m)'

                    else:
                        ylabel = data[sorted_data[i][0]].ax.get_ylabel()

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
                mpl.rcParams['savefig.directory'] = '/home/jaime/Documents/My Papers/Ongoing/Current Reflections/LaTex/Pictures/Temp/'

                x = data[meass].dataTime
                y = data[meass].data

                y_filtered = filters.moving_average(y, window)

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

                    p = df.RelativeTimePlot(x, y)
                    p.plot()

                    plt.show()

                    peak = y[p.zero_ind]

                    norm_factor = float(peak - zero)*factor

                fig = plt.figure()
                ax = fig.add_subplot(111)

                zoom_lim = [-1, int(lim)]

                # title = '%s (RS #%d)' % (self.eventName, r_s)
                # title = '%s (ICC)' % self.eventName
                title = data[meass].ax.get_title()

                if factor == 1E-3:
                    ylabel = '(k%s' % (data[meass].ax.get_ylabel()[1:])
                else:
                    ylabel = data[meass].ax.get_ylabel()

                xlabel = 'Time ($\mu$s)'

                ax.plot(x, y_filtered*factor/norm_factor, linewidth=l_width)
                ax.set_title(title)
                #~ ax.set_ylabel(ylabel)
                #~ ax.set_xlabel(xlabel)
                ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
                ax.grid(True, which='both')
                ax.xaxis.set_tick_params(width=1.5)
                #~ ax.autoscale(True,'y')
                ax.set_xlim(zoom_lim)
                #~ ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())

                p = df.pickerPlot(fig, ax)
                p.plot()

            plt.show()

    def save_data(self, fileSave):
        print("Saving data to: {file}".format(file=fileSave))
        if self.data:
            if self.fo:
                file_data = self.fo
                file_data.update(self.data)
            else:
                file_data = self.data

            pickle.dump(file_data, open(fileSave, "wb"))

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

            fileSave = "./DataFiles/%s_data_%s_rs%d_oo.p" % (self.eventNamef,
                                                          self.eventDate, r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS #%d:' % (self.eventName, r_s)

            keys = data.keys()

            print(event)

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

            fileSave = "./DataFiles/%s_data_%s_rs%d_oo.p" % (self.eventNamef,
                                                             self.eventDate,
                                                             r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass].data
                time = data[meass].dataTime*1.0E-6

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

            fileSave = "./DataFiles/%s_data_%s_rs%d_oo.p" % (self.eventNamef,
                                                          self.eventDate,
                                                          r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = data[meass].data
                ii = self.moving_average(ii, window)
                time = data[meass].dataTime*1.0E-6

                fig, ax = plt.subplots(1, 1)
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

            fileSave = "./DataFiles/%s_data_%s_rs%d_oo.p" % (self.eventNamef,
                                                          self.eventDate, r_s)
            data = pickle.load(open(fileSave, "rb"))

            event = '%s RS%d' % (self.eventName, r_s)

            keys = data.keys()

            if meass in keys:

                ii = self.moving_average(data[meass].data, window)
                time = data[meass].dataTime*1.0E-6

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
