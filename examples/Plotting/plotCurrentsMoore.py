#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.io import savemat as svmat

import JaimePackages.oscilloscopes.yoko850 as yk
import JaimePackages.plotting.dfplots as df

filename = "/media/jaime/ICLRTArray/2015Data/082715/Scope24/UF1543_IIHI"
# filename = "/media/jaime/ICLRTArray/2015Data/082715/Scope24/UF1542_IIHI"

f = yk.Yoko850File(filename)
header = f.get_header()

results = f.get_trace_data(header,1,0.5,1.5,19900.50,'y')

I = results.data
t = results.dataTime

rp = df.RelativeTimePlot(t,I*1E-3)
rp.plot()

plt.show()

rp.relative_plot(1E6, [250E-6, 1E-3])
plt.show()

# Save .mat file
bounds = [250E-6, 1E-3]
lbound = rp.zero_time - bounds[0]
rbound = rp.zero_time + bounds[-1]

time = rp.x[int((lbound - rp.x[0])/rp.delta_t):int((rbound - rp.x[0])/rp.delta_t)]
wave = rp.y[int((lbound - rp.x[0])/rp.delta_t):int((rbound - rp.x[0])/rp.delta_t)]

data = {}
data['time'] = time
data['data'] = wave

svmat('./UF1543_RS1.mat', data)

# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot(t,I*1E-3)
# ax.set_xlabel("Time (sec)")
# ax.set_ylabel("I (kA)")

plt.show()
