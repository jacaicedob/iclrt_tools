#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt

events = ['UF15-38',
          'UF15-39',
          'UF15-40',
          'UF15-41',
          'UF15-42',
          'UF15-43']

radar_files = ['/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_232606_V06.gz',
               '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_233020_V06.gz',
               '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_234304_V06.gz',
               '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_234304_V06.gz',
               '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_234727_V06.gz',
               '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/KJAX20150827_235145_V06.gz']

lma_files = ['/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_232000_0600_8stations.dat',
             '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_233000_0600_8stations.dat',
             '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_234000_0600_8stations.dat',
             '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_234000_0600_8stations.dat',
             '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_234000_0600_8stations.dat',
             '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/LMA/LYLOUT_150827_235000_0600_8stations.dat']

times = [['23:24:26.12', '23:24:26.798'],
         ['23:32:06.23', '23:32:06.768'],
         ['23:41:20.32', '23:41:20.9802'],
         ['23:43:56.71', '23:43:57.5924'],
         ['23:47:42.266', '23:47:43.3979'],
         ['23:53:22.251', '23:53:23.7634']]

zlims = [[0, 6],
         [0, 7],
         [0, 8],
         [0, 7.5],
         [0, 7],
         [0, 8]]

for i, event in enumerate(events):
    print(event)

    print("  Reading LMA file...")
    lma_plotter = df.LMAPlotter(lma_files[i])

    print("  Reading radar file...")
    radar_plotter = df.RadarPlotter(radar_files[i])

    print("  Filtering LMA dada...")
    lma_plotter.filter_time(times[i])
    lma_plotter.filter_rc2(1.0)
    lma_plotter.filter_xy([-20e3, 20E3], [-20E3, 20E3])
    lma_plotter.filter_num_stations(6)

    print("  Plotting...")
    lma_plotter.plot_alt_t(lims=[zlims[i][0], zlims[i][1]*1e3])

    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_ppi('reflectivity', fig=fig, ax=ax)
    ax.set_title('Base Reflectivity Z (Plan)')
    lma_plotter.scale_data(1E-3)
    lma_plotter.set_cmap('grey')
    lma_plotter.plot_plan(fig=fig, ax=ax, xlims=[-20, 20], ylims=[-20, 20])

    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_pseudo_rhi('reflectivity', fig=fig, ax=ax)
    ax.set_title('Base Reflectivity Z (RHI)')
    lma_plotter.set_cmap('grey')
    lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)

    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_pseudo_rhi('differential_reflectivity', fig=fig, ax=ax)
    ax.set_title(r'Differential Reflectivity $Z_{DR}$ (RHI)')
    lma_plotter.set_cmap('grey')
    lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)

    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_pseudo_rhi('cross_correlation_ratio', fig=fig, ax=ax)
    ax.set_title(r'Cross Correlation Ratio $\rho_{HV}$ (RHI)')
    lma_plotter.set_cmap('grey')
    lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)

    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_pseudo_rhi('differential_phase', fig=fig, ax=ax)
    ax.set_title(r'Differential Phase $\phi_{DP}$ (RHI)')
    lma_plotter.set_cmap('grey')
    lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)

    plt.show()
