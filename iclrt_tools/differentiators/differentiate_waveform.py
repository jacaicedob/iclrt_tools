#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
import matplotlib.pyplot as plt

import iclrt_tools.plotting.dfplots as df


def differentiate(dataTime, data):

    """
    Add code to take out the dc offset
    """

    wave = data
    t = dataTime

    delta_t = np.diff(t)[0]

    d_dt = np.gradient(wave, delta_t)

    return dataTime, d_dt, wave
