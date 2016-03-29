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
# p.filter_time(['22:37:24.0', '22:37:25.0'])

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