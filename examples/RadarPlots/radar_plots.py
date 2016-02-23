#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt
import os
import sys

parent = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/'

os.chdir(parent)
radar_files = ['./KJAX20150827_233020_V06.gz',
               './KJAX20150827_211322_V06.gz',
               './KJAX20150827_211732_V06.gz',
               './KJAX20150827_212210_V06.gz',
               './KJAX20150827_212610_V06.gz',
               './KJAX20150827_213013_V06.gz',
               './KJAX20150827_213427_V06.gz',
               './KJAX20150827_213833_V06.gz',
               './KJAX20150827_214240_V06.gz',
               './KJAX20150827_214645_V06.gz',
               './KJAX20150827_215051_V06.gz',
               './KJAX20150827_215457_V06.gz',
               './KJAX20150827_215904_V06.gz',
               './KJAX20150827_220504_V06.gz',
               './KJAX20150827_220911_V06.gz',
               './KJAX20150827_221316_V06.gz',
               './KJAX20150827_221717_V06.gz',
               './KJAX20150827_222109_V06.gz',
               './KJAX20150827_222508_V06.gz',
               './KJAX20150827_222904_V06.gz',
               './KJAX20150827_223257_V06.gz',
               './KJAX20150827_223653_V06.gz',
               './KJAX20150827_224048_V06.gz',
               './KJAX20150827_224444_V06.gz',
               './KJAX20150827_224841_V06.gz',
               './KJAX20150827_225237_V06.gz',
               './KJAX20150827_225655_V06.gz',
               './KJAX20150827_230052_V06.gz',
               './KJAX20150827_230448_V06.gz',
               './KJAX20150827_230857_V06.gz',
               './KJAX20150827_231312_V06.gz',
               './KJAX20150827_231743_V06.gz',
               './KJAX20150827_232152_V06.gz',
               './KJAX20150827_232606_V06.gz',
               './KJAX20150827_233020_V06.gz',
               './KJAX20150827_233429_V06.gz',
               './KJAX20150827_233844_V06.gz',
               './KJAX20150827_234304_V06.gz',
               './KJAX20150827_234727_V06.gz',
               './KJAX20150827_235145_V06.gz',
               './KJAX20150827_235619_V06.gz',
               './KJAX20150828_000055_V06.gz',
               './KJAX20150828_000514_V06.gz',
               './KJAX20150828_000933_V06.gz',
               './KJAX20150828_001417_V06.gz',
               './KJAX20150828_001904_V06.gz',
               './KJAX20150828_002343_V06.gz',
               './KJAX20150828_002826_V06.gz',
               './KJAX20150828_003310_V06.gz',
               './KJAX20150828_003748_V06.gz',
               './KJAX20150828_004231_V06.gz',
               './KJAX20150828_004713_V06.gz',
               './KJAX20150828_005151_V06.gz',
               './KJAX20150828_005630_V06.gz']

parent = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 07-17-2012/Radar Data/KJAX'
os.chdir(parent)

radar_files = ['./KJAX_SDUS52_N0RJAX_201207171803',
               './KJAX_SDUS52_N0RJAX_201207171808',
               './KJAX_SDUS52_N0RJAX_201207171812',
               './KJAX_SDUS52_N0RJAX_201207171817',
               './KJAX_SDUS52_N0RJAX_201207171822',
               './KJAX_SDUS52_N0RJAX_201207171827',
               './KJAX_SDUS52_N0RJAX_201207171831',
               './KJAX_SDUS52_N0RJAX_201207171836',
               './KJAX_SDUS52_N0RJAX_201207171841',
               './KJAX_SDUS52_N0RJAX_201207171845',
               './KJAX_SDUS52_N0RJAX_201207171850',
               './KJAX_SDUS52_N0RJAX_201207171855',
               './KJAX_SDUS52_N0RJAX_201207171900',
               './KJAX_SDUS52_N0RJAX_201207171904',
               './KJAX_SDUS52_N0RJAX_201207171909',
               './KJAX_SDUS52_N0RJAX_201207171914',
               './KJAX_SDUS52_N0RJAX_201207171918',
               './KJAX_SDUS52_N0RJAX_201207171923',
               './KJAX_SDUS52_N0RJAX_201207171928',
               './KJAX_SDUS52_N0RJAX_201207171932',
               './KJAX_SDUS52_N0RJAX_201207171937',
               './KJAX_SDUS52_N0RJAX_201207171942',
               './KJAX_SDUS52_N0RJAX_201207171947',
               './KJAX_SDUS52_N0RJAX_201207171951',
               './KJAX_SDUS52_N0RJAX_201207171956',
               './KJAX_SDUS52_N0RJAX_201207172001',
               './KJAX_SDUS52_N0RJAX_201207172005',
               './KJAX_SDUS52_N0RJAX_201207172010',
               './KJAX_SDUS52_N0RJAX_201207172015',
               './KJAX_SDUS52_N0RJAX_201207172020',
               './KJAX_SDUS52_N0RJAX_201207172024',
               './KJAX_SDUS52_N0RJAX_201207172029',
               './KJAX_SDUS52_N0RJAX_201207172034',
               './KJAX_SDUS52_N0RJAX_201207172039',
               './KJAX_SDUS52_N0RJAX_201207172044',
               './KJAX_SDUS52_N0RJAX_201207172048',
               './KJAX_SDUS52_N0RJAX_201207172053',
               './KJAX_SDUS52_N0RJAX_201207172058',
               './KJAX_SDUS52_N0RJAX_201207172102',
               './KJAX_SDUS52_N0RJAX_201207172107',
               './KJAX_SDUS52_N0RJAX_201207172111',
               './KJAX_SDUS52_N0RJAX_201207172116',
               './KJAX_SDUS52_N0RJAX_201207172121',
               './KJAX_SDUS52_N0RJAX_201207172126',
               './KJAX_SDUS52_N0RJAX_201207172130',
               './KJAX_SDUS52_N0RJAX_201207172135',
               './KJAX_SDUS52_N0RJAX_201207172140',
               './KJAX_SDUS52_N0RJAX_201207172144',
               './KJAX_SDUS52_N0RJAX_201207172149',
               './KJAX_SDUS52_N0RJAX_201207172154',
               './KJAX_SDUS52_N0RJAX_201207172159']

for radar_file in radar_files:
    print("Reading radar file: " + radar_file)
    radar_plotter = df.RadarPlotter(radar_file)

    print("  - Plotting")
    fig, ax = plt.subplots(1, 1)
    radar_plotter.plot_ppi('reflectivity', fig=fig, ax=ax)
    ax.scatter(0, 0, s=50, c='w')
    ax.set_xlim([-40, 40])
    ax.set_ylim([-40, 40])
    ax.set_xlabel('West - East (km)')
    ax.set_ylabel('South - North (km)')
    # ax.set_title(radar_file[2:-7])
    # save_file = './PNG/' + radar_file[2:-2] + 'png'
    ax.set_title(radar_file[2:])
    save_file = './PNG/' + radar_file[2:] + '.png'
    fig.savefig(save_file, dpi=300, format='png')

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

    # radar_plotter.plot_ppi_rhi()
    # plt.show()