#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import all other modules
import iclrt_tools.field_mill.field_mill as fm
import iclrt_tools.plotting.dfplots as df

import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import numpy as np

def date_format_major(x, pos=None):
    x = mpl.dates.num2date(x)

    if pos == 0 or pos == -1:
        fmt = '%H:%M:%S.%f'

    else:
        fmt = '%H:%M:%S.%f'

    label = x.strftime(fmt)
    ind_dot = label.find('.')
    label = label[:ind_dot+5]
    label = label.rstrip('0')
    label = label.rstrip('.')

    return label

def date_format_minor(x, pos=None):
    x = mpl.dates.num2date(x)

    fmt = '%H:%M:%S.%f'

    label = x.strftime(fmt)
    ind_dot = label.find('.')
    label = label[:ind_dot+5]
    label = label.rstrip('0')
    label = label.rstrip('.')

    return label


file_name = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/FieldMill/Launch Control_Tab60.dat'

file_name2 = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/FieldMill/Office Trailer_Tab60.dat'

f = fm.FieldMillData(file_name)
f2 = fm.FieldMillData(file_name2)

f.filter_time(['21:46:45.0', '22:44:44.0'])
f2.filter_time(['21:46:45.0', '22:44:44.0'])

t = f.t
fair_field = np.average(f.E[:int(len(f.E)/10)])
fair_field2 = np.average(f2.E[:int(len(f2.E)/10)])

target_time = datetime.datetime.strptime('22:37:24.7', '%H:%M:%S.%f')
target_time = datetime.datetime(f.t[0].year, f.t[0].month, f.t[0].day,
                                target_time.hour, target_time.minute,
                                target_time.second, target_time.microsecond)
ind = np.argmin(np.abs(target_time - f.t))
print(ind)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
ax1.plot(f.t, f.E)
ax2.plot(f2.t, f2.E)
ax1.scatter(f.t[ind], f.E[ind], marker='x', c='red')
ax2.scatter(f.t[ind], f.E[ind], marker='x', c='red')

ax1.plot([target_time, target_time],
         [ax1.get_ylim()[0], ax1.get_ylim()[1]], '--r')
ax2.plot([target_time, target_time],
         [ax2.get_ylim()[0], ax2.get_ylim()[1]], '--r')

ax1.plot([ax1.get_xlim()[0], ax1.get_xlim()[1]],
         [fair_field, fair_field], '--r')
ax2.plot([ax2.get_xlim()[0], ax2.get_xlim()[1]],
         [fair_field2, fair_field2], '--r')

ax2.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(10))

plt.show()
