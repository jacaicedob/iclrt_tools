#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import all other modules
import iclrt_tools.field_mill.field_mill as fm
import iclrt_tools.plotting.dfplots as df

import matplotlib.pyplot as plt

file_name = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/FieldMill/Launch Control_TabFast.dat'

file_name2 = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/FieldMill/Office Trailer_TabFast.dat'

f = fm.FieldMillData(file_name)
f2 = fm.FieldMillData(file_name2)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
ax1.plot(f.t, f.E)
ax2.plot(f2.t, f2.E)
plt.show()
