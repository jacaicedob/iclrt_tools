#!/usr/bin/env python

import sys
import iclrt_tools.plotting.dfplots as df
import iclrt_tools.oscilloscopes.lecroy as lc
import iclrt_tools.oscilloscopes.yoko750 as yk750
import iclrt_tools.oscilloscopes.yoko850 as yk850

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy import interpolate


def moving_average(y, n=5.0):
    weights = np.repeat(1.0, n)/n
    sma = np.convolve(y, weights, 'same')
    return sma

def integrate_cumtrapz(y, x, average=False, window=5.0):
    
    if average:
        y = moving_average(y, window)

    return integrate.cumtrapz(y=y, x=x, initial=0.0)


def integ(x, spline, constant=-1):
    x = np.atleast_1d(x)
    out = np.zeros(x.shape, dtype=x.dtype)
    
    for n in range(len(out)):
        out[n] = interpolate.splint(0, x[n], spline)
    out += constant
    
    return out
    
    
def integrate_simps(y, x, average=False, window=5.0):
    
    if average:
        y = moving_average(y, window)
        
    output = np.zeros(len(y))
    
    j = 1
    n = 10000
    for i in range(n):
        
        output[j] = integrate.simps(y[0:j], x[0:j])
        j += int(len(y)/float(n))
        
    return output
    
