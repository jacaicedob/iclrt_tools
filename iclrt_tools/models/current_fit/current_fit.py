#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other packages
import numpy as np
import matplotlib.pyplot as plt
import scipy
import matplotlib as mpl
import operator
import pickle
import xml.etree.ElementTree as ET

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.yoko850 as yk


class CurrentFitTail(object):
    """
    Fits an exponential tail to a portion of a RS current.
    """
    
    def __init__(self, t, i, tau=20.0E-6):
        self.t = t
        self.i = i
        self.tau = tau
        
    def fit(self):
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.t, self.i)
        ax.set_ylabel("I (A)")
        ax.set_xlabel("Time (sec)")
        ax.set_title("Select the fitting point while pressing 'o'")

        self.p = df.Plot(fig, ax, max_points=np.inf)
        self.p.plot()

        plt.show()

        # Get the time values for the zoom and use them to get the cropped arrays
        self.delta_t = np.diff(self.t)[0]

        print(self.p.points, self.delta_t)

        sel_li, sel_fi = np.searchsorted(self.t, (self.p.ax.get_xlim()[0], self.p.points[0][0]))
        
        print(sel_li, sel_fi)

        # sel_li = 0
        ii = self.i[sel_li:sel_fi]
        tt = self.t[sel_li:sel_fi] - self.t[sel_li]
        
        plt.plot(tt, ii)
        plt.show()

        ### Fit a tail to the curve and append it

        # Find the index of the peak and its value
        #~ n_peak, ii_peak = max(enumerate(ii), key=operator.itemgetter(1))

        t_max_tail = 20E-3 #100.0E-6
        t_array_tail = np.arange(0, t_max_tail, self.delta_t)

        tail = ii[-1] * np.exp(-t_array_tail/self.tau)
        
        #~ plt.plot(tail)
        #~ plt.show()

        ii_final = np.append(ii[:-1], tail)
        tt_final = np.append(tt[:-1], t_array_tail+tt[-1])

        #~ plt.plot(tt_final, ii_final)
        #~ plt.show()

        ### Smooth out the signal using a Savitzky-Golay filter
        #~ from scipy.signal import savgol_filter
        #~ ii_savgol = savgol_filter(ii_final, 9, 5)

        #~ plt.plot(tt_final, ii_final)
        #~ plt.plot(tt_final, ii_savgol, 'r')
        #~ plt.show()
        
        self.i = ii_final#ii_savgol
        self.t = tt_final
        self.ind = sel_fi - sel_li
    

class CurrentFitDecay(object):
    """
    Finds the exponential fit of the decay portion of the return stroke
    prior to the dip and this fit is used to extend the curve for the
    length of the measured waveform for comparison.
    """
    def __init__(self, t, i, diff=None):
        self.t = t
        self.i = i
        self.diff = diff

    def fit(self):
        fig, ax = plt.subplots(1, 1)
        ax.plot(self.t, self.i)
        ax.set_title("Select boundaries of region to fit")
        p = df.Plot(fig, ax)
        plt.show()

        xmin = p.points[0][0]
        xmax = p.points[1][0]

        indmin, indmax = np.searchsorted(self.t, (xmin, xmax))
        decay_y = self.i[indmin:indmax]
        decay_x = self.t[indmin:indmax]

        m, b, r, p, err = scipy.stats.linregress(decay_x, np.log(decay_y))
        self.fitted_params = {'m': m, 'b': b, 'r2': r*r, 'p': p, 'stderr': err}
        t_fitted = self.t[indmin:]
        fitted = np.exp(m * t_fitted + b)

        offset = self.i[indmin] - fitted[0]

        self.fitted = np.append(self.i[:indmin], fitted + offset)

        print(self.fitted_params)

    def plot_fit_vs_measure(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        if self.diff is None:
            self.diff = 0.03 * self.fitted

        ax.plot(self.t, self.i, self.t, self.fitted, self.t, (self.fitted - self.i), [self.t[0], self.t[-1]], [0, 0], [self.t[0], self.t[-1]], [self.diff, self.diff], '--', [self.t[0], self.t[-1]], [-self.diff, -self.diff], '--')

        # ax.set_xlim([-2e-6, 25e-6])

        df.Plot(fig, ax)
        plt.show()
