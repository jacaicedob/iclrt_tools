#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt

radar_file = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_233020_V06.gz'
lma_file = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_233000_0600_8stations.dat'

print("Reading LMA file...")
lma_plotter = df.LMAPlotter(lma_file)

print("Reading radar file...")
radar_plotter = df.RadarPlotter(radar_file)

print("Filtering LMA dada...")
lma_plotter.filter_time(['23:32:06.20', '23:32:06.77'])
lma_plotter.filter_rc2(1.0)
lma_plotter.filter_xy([-20e3, 20E3], [-20E3, 20E3])
lma_plotter.filter_num_stations(6)

print("Plotting...")
fig, ax = plt.subplots(1, 1)
radar_plotter.plot_ppi('reflectivity', fig=fig, ax=ax)
lma_plotter.plot_alt_t()
lma_plotter.scale_data(1E-3)
lma_plotter.set_cmap('grey')
lma_plotter.plot_plan(fig=fig, ax=ax, xlims=[-20, 20], ylims=[-20, 20])

fig, ax = plt.subplots(1, 1)
lma_plotter.scale_data(1E3)
radar_plotter.plot_pseudo_rhi('reflectivity', fig=fig, ax=ax)
lma_plotter.scale_data(1E-3)
lma_plotter.set_cmap('grey')
lma_plotter.plot_proj(lims=[-20, 20], zlims=[0, 7], fig=fig, ax=ax)

plt.show()
