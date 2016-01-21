#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import custom modules from the new system path
import iclrt_tools.oscilloscopes.lecroy as lc
import iclrt_tools.oscilloscopes.yoko850 as yk850
import iclrt_tools.integrators.integrate_waveform as integrators
import iclrt_tools.filters.filters as filters
import iclrt_tools.plotting.dfplots as df

# Import other modules
import numpy as np
import sys
import matplotlib.pyplot as plt


class Waveform(object):
    def __init__(self, flash_name, event_date, return_stroke,
                 measurement_name, scope_name, scope_type, file_name,
                 trace_number, cal_factor, units, distance, t_start,
                 t_end):

        self.flash_name = flash_name
        self.date = event_date
        self.return_stroke = return_stroke
        self.measurement_name = measurement_name
        self.scope_name = scope_name
        self.scope_type = scope_type
        self.file_name = file_name
        self.trace_number = trace_number
        self.cal_factor = cal_factor
        self.units = units
        self.distance = distance
        self.t_start = t_start
        self.t_end = t_end
        self.data = None
        self.dataTime = None
        self.noise_mean = None
        self.noise_sigma = None

    def __str__(self):
        s = ""
        s += "Waveform information:\n"
        s += "-" * 80
        s += "Flash: {event}\n".format(event=self.flash_name)
        s += "Date: {date}\n".format(date=self.date)
        s += "Return stroke number: {rs}\n".format(rs=self.return_stroke)
        s += "Measurement: {name}\n".format(name=self.measurement_name)
        s += "Measurement distance (m): {distance}\n".format(
             distance=self.distance)
        s += "Scope Name: {name}\n".format(name=self.scope_name)
        s += "Scope Type: {scope}\n".format(scope=self.scope_name)
        s += "File location: {file}\n".format(file=self.file_name)
        s += "Trace number: {trace:d}\n".format(trace=self.trace_number)
        s += "Cal factor: {cal:0.2f}\n".format(cal=self.cal_factor)
        s += "Units: {units}\n".format(units=self.units)
        s += "Start time in file: {t_start}\n".format(t_start=self.t_start)
        s += "End time in file: {t_end}\n".format(t_end=self.t_end)

        return s

    def read_yoko(self, wantOffset):
        f = yk850.Yoko850File(self.file_name)
        header = f.get_header()

        try:
            data = f.get_trace_data(header, self.trace_number,
                                    self.t_start, self.t_end,
                                    self.cal_factor, wantOffset)

            self.dataTime = data.dataTime
            self.data = data.data

        except AttributeError:
            print("\n\nERROR: Invalid file.")
            sys.exit(1)

    def read_lecroy(self, wantOffset=False):
        lecroy = lc.lecroy_data(self.file_name)
        lecroy.get_seg_time()
        lecroy.get_segment(self.trace_number, self.cal_factor)

        if wantOffset:
            offset = np.average(lecroy.data[0:int(len(lecroy.data)/5)])
            lecroy.data -= offset

        self.data = lecroy.data
        self.dataTime = lecroy.dataTime

    def get_data(self, lims=[5E-6, 295E-6], wantOffset=False):
        if "yoko" in self.scope_type.lower():
            self.read_yoko(wantOffset)
        elif "lecroy" in self.scope_type.lower():
            self.read_lecroy(wantOffset)
        else:
            raise IOError('Unknown scope type.')

        # Smooth out LOG and GOLF data
        if "log" in self.measurement_name.lower() or \
                        "golf" in self.measurement_name.lower():
            window_length = 5.0
            sma = filters.moving_average(self.data, window_length)

            self.data = sma

        # Integrate desired dE/dt waveforms
        if "int" in self.measurement_name.lower():
            self.data = integrators.integrate_cumtrapz(y=self.data,
                                                       x=self.dataTime,
                                                       initial=0)

        self.get_plot(lims)

    def get_plot(self, lims=None):
        # Get the desired time intervals
        rt_plot = df.RelativeTimePlot(self.dataTime, self.data,
                                      max_points=1E9)
        rt_plot.plot()
        plt.show()

        if "noise" in self.measurement_name.lower():
            fig, ax = rt_plot.relative_plot(1,
                                            [0, len(rt_plot.y) *
                                             rt_plot.delta_t])
        else:
            fig, ax = rt_plot.relative_plot(1, lims)

        fig = fig
        ax = ax

        if "int" in self.measurement_name.lower():
            ax.set_title('%s (D = %sm)' %
                              ('Integrated d%s' % self.measurement_name[3:],
                               self.distance))
        else:
            ax.set_title('%s (D = %sm)' % (self.measurement_name,
                                                self.distance))

        ax.set_ylabel('(%s)' % self.units)
        plt.close(fig)

        self.data = ax.get_lines()[0].get_ydata() - \
                    rt_plot.y[rt_plot.zero_ind]

        self.dataTime = ax.get_lines()[0].get_xdata()

    def set_data(self, data):
        self.data = data

    def set_dataTime(self, time):
        self.dataTime = time

    def calc_noise_level(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.dataTime, self.data)
        ax.set_title('Select noise region')

        p = df.Plot(fig, ax)
        plt.show()

        if len(p.points) > 2:
            print('Error! Only select 2 points.')
            return None

        xs = [pt[0] for pt in p.points]
        xs.sort()

        indmin, indmax = np.searchsorted(self.dataTime, (xs[0], xs[1]))
        indmax = min(len(self.dataTime)-1, indmax)
        self.noise_mean = np.mean(self.data[indmin:indmax])
        self.noise_sigma = np.std(self.data[indmin:indmax])

        # Set offset to the noise mean
        self.data -= self.noise_mean

        self.noise_rms = np.sqrt(self.noise_mean**2 + self.noise_sigma**2)
        # return self.noise_mean, self.noise_sigma

    def calc_point_above_noise(self, mult=5):
        if not(self.noise_sigma) or not(self.noise_mean):
            self.calc_noise_level()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.dataTime, self.data)
        ax.set_title(r'Select region to find point above $%d\sigma$'%mult)

        p = df.Plot(fig, ax)
        plt.show()

        points = p.points

        indmin, indmax = np.searchsorted(self.dataTime,
                                         (points[0][0], points[1][0]))

        data = self.data[indmin:indmax]

        ind = np.argmax(np.abs(1.0 / (mult*self.noise_sigma - data)))
        t_above = self.dataTime[indmin + ind]
        y_above = self.data[indmin + ind]

        self.ind_above_noise = indmin + ind
        print('Value above 5 sigma: ({}, {})'.format(t_above, y_above))
        return t_above, y_above, indmin + ind

    def plot_noise_analysis(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.dataTime, self.data)
        ax.plot(ax.get_xlim(), [self.noise_sigma*mult, self.noise_sigma*mult],
                '--r')
        ax.plot(ax.get_xlim(), [0, 0], 'r')
        ax.plot(ax.get_xlim(), [-self.noise_sigma*mult, -self.noise_sigma*mult],
                '--r')

        ax.scatter(self.dataTime[self.ind_above_noise], self.data[self.ind_above_noise])

        p = df.Plot(fig, ax)
        p.plot()

        plt.show()

        if p.points:
            return p.points

    def peak_to_peak(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.dataTime, self.data)
        ax.set_title('Select peak region')

        p = df.Plot(fig, ax)
        plt.show()

        if len(p.points) > 2:
            print('Error! Only select 2 points.')
            return None

        xs = [pt[0] for pt in p.points]
        xs.sort()

        indmin, indmax = np.searchsorted(self.dataTime, (xs[0], xs[1]))
        indmax = min(len(self.dataTime)-1, indmax)

        data = self.data[indmin:indmax]
        time = self.dataTime[indmin:indmax]

        indmin1 = np.argmin(data)
        indmax1 = np.argmax(data)

        plt.plot(self.dataTime, self.data)
        plt.scatter(self.dataTime[indmin+indmin1], self.data[indmin+indmin1])
        plt.scatter(self.dataTime[indmin+indmax1], self.data[indmin+indmax1])
        print(time[indmax1] - time[indmin1])
        p = df.Plot(plt.gcf(), plt.gca())
        plt.show()

        # xs = [pt[0] for pt in p.points]
        # xs.sort()
        #
        # indmin2 = np.searchsorted(self.dataTime, xs[0])
        # print(time[indmax1] - self.dataTime[indmin2])



