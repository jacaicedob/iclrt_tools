#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other packages
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator

import JaimePackages.plotting.dfplots as df
import JaimePackages.oscilloscopes.lecroy as lc
import JaimePackages.timing.timing as timing

file_name = "./C4AC00001.trc"

#~ x,y = lc.read_timetrace(file_name)
lecroy = lc.lecroy_data(file_name)

seg_time = lecroy.get_seg_time()
segments = lecroy.get_segments()

n_ticks = 1.0

mult, string = timing.fix_time(seg_time, n_ticks)
#~     mult = 1
#~     string = ''

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(seg_time*mult, segments[0])
ax.set_title('Segment 1')
ax.set_xlabel('Time (%s)' % string)
ax.set_xlim([seg_time[0]*mult, seg_time[-1]*mult])
ax.xaxis.set_major_locator(LinearLocator(numticks=n_ticks))
#  ax.xaxis.set_ticks()
#~ ax.locator_params(axis='x', nbins=200)
#~ ax.locator_params(axis='y', nbins=10)
#~ ax.locator_params(tight=True)


#~ i = 1
#~ plt.figure()
#~
#~ for segment in segments:
#~     plt.subplot(len(segments),1,i)
#~     plt.plot(seg_time*1E3,segment)
#~     plt.title("%s Segment %d" % (lecroy.get_timestamp().strftime('%Y-%m-%d %H:%M:%S.%f'),i))
#~     i += 1

plt.show()
