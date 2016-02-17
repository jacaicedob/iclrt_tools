#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt

radar_file = './Data/KJAX20150819_223952_V06'
lma_file = './Data/LYLOUT_150819_224000_0600_8stations.dat'

print("Reading LMA file...")
lma_plotter = df.LMAPlotter(lma_file)

print("Reading radar file...")
radar_plotter = df.RadarPlotter(radar_file)

print("Filtering LMA dada...")
lma_plotter.filter_time(['22:40:22.0', '22:40:24.1'])
lma_plotter.filter_rc2(1.0)
lma_plotter.filter_xy([-100E3, 100E3], [-100E3, 100E3])
lma_plotter.filter_num_stations(6)

print("Plotting...")
fig, ax = plt.subplots(1, 1)
radar_plotter.plot_ppi('reflectivity', fig=fig, ax=ax)
lma_plotter.scale_data(1E-3)
lma_plotter.set_cmap('grey')
lma_plotter.plot_plan(fig=fig, ax=ax, xlims=[-100, 100], ylims=[-100, 100])
plt.show()
