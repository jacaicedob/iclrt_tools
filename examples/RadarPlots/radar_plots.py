#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt
import sys
import math

sys.path.append('/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Figures/')

from radar_start_to_first_flash import *

for radar_file in radar_files:
    print("Reading radar file: " + radar_file)
    radar_plotter = df.RadarPlotter(radar_file)
    # radar_plotter.setup_display(shift=[0, 0])

    print("  - Plotting")
    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_ppi('reflectivity', fig=fig, ax=ax)
    # ax.scatter(0, 0, s=50, c='w')
    # ax.set_xlim([-40, 40])
    # ax.set_ylim([-40, 40])
    # ax.set_xlabel('West - East (km)')
    # ax.set_ylabel('South - North (km)')
    # # ax.set_title(radar_file[2:-7])
    # # save_file = './PNG/' + radar_file[2:-2] + 'png'
    # ax.set_title(radar_file[2:])
    # save_file = './PNG/' + radar_file[2:] + '.png'
    # fig.savefig(save_file, dpi=300, format='png')

    # fig, ax = plt.subplots(1,3)
    # radar_plotter.plot_pseudo_rhi('reflectivity', azimuth=188.71, fig=fig, ax=ax[0])
    # radar_plotter.plot_pseudo_rhi('reflectivity', fig=fig, ax=ax[1])
    # radar_plotter.plot_pseudo_rhi('reflectivity', azimuth=232.64, fig=fig, ax=ax[2])
    # ax[0].set_xlim([-20, 80])
    # ax[0].set_ylim([0, 20])
    # ax[1].set_xlim([-20, 80])
    # ax[1].set_ylim([0, 20])
    # ax[2].set_xlim([-20, 80])
    # ax[2].set_ylim([0, 20])
    # plt.show()

    # line, = ax.plot([0], [0], 'k')
    # line.set_data([radar_plotter.ICLRT_shift[0]/1e3,
    #                radar_plotter.ICLRT_shift[0]/1e3 - 200*math.cos((
    #                                                  270-212.053)*math.pi/180)],
    #               [radar_plotter.ICLRT_shift[1]/1e3,
    #                radar_plotter.ICLRT_shift[1]/1e3 - 200*math.sin((
    #                                                   270-212.053)*math.pi/180)])
    #
    #
    # fig, ax = plt.subplots(1, 1)
    # radar_plotter.plot_pseudo_rhi(azimuth=212.053, fig=fig, ax=ax)
    # ax.set_xlim([-48, 60])
    # ax.set_ylim([0, 20])
    # ax.set_title(radar_file[2:])
    # plt.show()

    radar_plotter.plot_ppi_rhi()
    plt.show()
