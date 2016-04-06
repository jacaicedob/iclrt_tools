#!/usr/bin/env python

# Add personal packages directory to path
import sys
import matplotlib.pyplot as plt
import datetime
import matplotlib as mpl

# Import custom module
import iclrt_tools.lma.lma as lma
import iclrt_tools.plotting.dfplots as df

fileName = '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_235318_0008_8stations.dat'

fileName = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/ChargeAnalysis-1of2-exported.dat'

fileName = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_223000_0600_8stations.dat'

fileName = '/home/jaime/Documents/LMA/Data/Triggered/2014/071414/UF14-26/LYLOUT_140714_190754_0008.dat'

fileName = '/home/jaime/Documents/LMA/Data/Triggered/2015/150827/LYLOUT_150827_232422_0008_8stations.dat'

print("Reading File...")
start = datetime.datetime.now()
f = lma.LMAFile(fileName, shift=(0, 0))
# f = lma.XLMAExportedFile(fileName)
print(datetime.datetime.now() - start)

start = datetime.datetime.now()
p = df.LMAPlotter(f)
print(datetime.datetime.now() - start)

print("Filtering...")

p.filter_rc2(1.0)
# p.filter_xy([-20E3, 20E3], [-20E3, 20E3])
p.filter_num_stations(7)
# p.filter_time(['23:24:25.9', '23:24:26.522908'])

### Moore's request to plot the RTL up to the point of each RS.
# times = [['23:24:24.900000', '23:24:26.522908'],
#          ['23:24:24.900000', '23:24:26.579535'],
#          ['23:24:24.900000', '23:24:26.691097'],
#          ['23:24:24.900000', '23:24:26.734557'],
#          ['23:24:24.900000', '23:24:26.764446'],
#          ['23:24:24.900000', '23:24:27.000000']]
#
# times = [['23:24:24.900000', '23:24:26.522908'],
#          ['23:24:26.522908', '23:24:26.579535'],
#          ['23:24:26.579535', '23:24:26.691097'],
#          ['23:24:26.691097', '23:24:26.734557'],
#          ['23:24:26.734557', '23:24:26.764446'],
#          ['23:24:26.764446', '23:24:27.000000']]
#
# name = ['IS',
#         'RS #1',
#         'RS #2',
#         'RS #3',
#         'RS #4',
#         'RS #5']
#
# for i in range(len(name)):
#     p.reset_filters()
#     p.filter_rc2(5.0)
#     p.filter_xy([-20E3, 20E3], [-20E3, 20E3])
#     p.filter_num_stations(7)
#     p.filter_time(times[i])
#     p.filter_alt(8e3)
#
#     fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
#     p.plot_plan(fig=fig, ax=ax1)
#     p.plot_proj('EW', zlims=[0, 8e3], fig=fig, ax=ax2)
#     p.plot_proj('NS', zlims=[0, 8e3], fig=fig, ax=ax3)
#
#     ax1.set_title('{0} - Plan View'.format(name[i]))
#     ax2.set_title('EW Projection')
#     ax3.set_title('NS Projection')
#
#     s = '{0} -- {1} UTC'.format(times[i][0][:-4], times[i][1][:-4])
#     ax1.text(-19e3, 14e3, s)
#
# plt.show()
# sys.exit(1)
###

print("Plotting...")

# p.set_cmap('grey')
# p.set_coloring('charge')
p.plot_alt_t()
plt.show()

# Get time and altitude limits and filter by them
t_lims = p.ax_alt_t.get_xlim()
t_lims = [datetime.datetime.strftime(mpl.dates.num2date(t_lims[0]), '%H:%M:%S.%f'), datetime.datetime.strftime(mpl.dates.num2date(t_lims[-1]), '%H:%M:%S.%f')]
z_lims = p.ax_alt_t.get_ylim()
z_lims = [0, 4e3]  #z_lims[-1]*1E3]

p.filter_time(t_lims)
p.filter_alt(z_lims[-1])

# Plot plan view
p.plot_plan()
plt.show()

# Get x,y lims and filter by them
x_lims = p.ax_plan.get_xlim()
y_lims = p.ax_plan.get_ylim()

p.filter_xy(x_lims, y_lims)

# p.plot_all()
# plt.show()

# Plot 3D
p.plot_3D(x_lims, y_lims, z_lims, projections=True)
plt.show()