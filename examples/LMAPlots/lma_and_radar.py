#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt
import sys

sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Figures/')
# from rtl_events import *
from start_to_first_flash import *

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

    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_pseudo_rhi('reflectivity', fig=fig, ax=ax)
    # ax.set_title('Base Reflectivity Z (RHI)')
    # lma_plotter.set_cmap('grey')
    # lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)
    #
    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_pseudo_rhi('differential_reflectivity', fig=fig, ax=ax)
    # ax.set_title(r'Differential Reflectivity $Z_{DR}$ (RHI)')
    # lma_plotter.set_cmap('grey')
    # lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)
    #
    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_pseudo_rhi('cross_correlation_ratio', fig=fig, ax=ax)
    # ax.set_title(r'Cross Correlation Ratio $\rho_{HV}$ (RHI)')
    # lma_plotter.set_cmap('grey')
    # lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)
    #
    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_pseudo_rhi('differential_phase', fig=fig, ax=ax)
    # ax.set_title(r'Differential Phase $\phi_{DP}$ (RHI)')
    # lma_plotter.set_cmap('grey')
    # lma_plotter.plot_proj(lims=[-20, 20], zlims=zlims[i], fig=fig, ax=ax)

    plt.show()
    