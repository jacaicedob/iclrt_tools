#!/usr/bin/env python

import numpy as np
from scipy.signal import butter, lfilter


def averaging_filter(x,t,n):
    """low-pass filter by averaging over n points"""
    x = np.convolve(x, np.ones((n,))/n, mode='valid')[:-1]
    t = t[int(n/2):-int(n/2)]
    return x, t

def moving_average(y, n=5):
    weights = np.repeat(1.0, n)/n
    sma = np.convolve(y, weights, 'same')
    return sma

def butter_lowpass(cutoff, sampling_rate, order=5):
    nyq = 0.5 * sampling_rate
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, sampling_rate, order=5):
    """ low-pass filter using a Butterworth filter """
    b, a = butter_lowpass(cutoff, sampling_rate, order=order)
    y = lfilter(b, a, data)
    return y
