#!/usr/bin/env python

import numpy as np
import scipy.integrate as integrate
from scipy import interpolate


def moving_average(y, n=5.0):
    weights = np.repeat(1.0, n)/n
    sma = np.convolve(y, weights, 'same')
    return sma

def integrate_cumtrapz(y, x, average=False, window=5.0, **kwargs):
    
    if average:
        y = moving_average(y, window)

    return integrate.cumtrapz(y=y, x=x, **kwargs)


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
