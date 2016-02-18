#!/usr/env python

import iclrt_tools.plotting.dfplots as df
import matplotlib.pyplot as plt
import os
import sys

parent = '/home/jaime/Documents/ResearchTopics/Publications/Lightning Evolution/Storm 08-27-2015/Radar/KJAX/Level-II/'

os.chdir(parent)
radar_files = ['./KJAX20150827_200226_V06.gz',
               './KJAX20150827_200618_V06.gz',
               './KJAX20150827_200957_V06.gz',
               './KJAX20150827_201337_V06.gz',
               './KJAX20150827_201715_V06.gz',
               './KJAX20150827_202111_V06.gz',
               './KJAX20150827_202519_V06.gz',
               './KJAX20150827_202906_V06.gz',
               './KJAX20150827_203250_V06.gz',
               './KJAX20150827_203630_V06.gz',
               './KJAX20150827_204049_V06.gz',
               './KJAX20150827_204441_V06.gz',
               './KJAX20150827_204833_V06.gz',
               './KJAX20150827_205235_V06.gz',
               './KJAX20150827_205631_V06.gz',
               './KJAX20150827_210032_V06.gz',
               './KJAX20150827_210433_V06.gz',
               './KJAX20150827_210911_V06.gz',
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
               './KJAX20150828_005630_V06.gz',
               './KJAX20150828_010118_V06.gz',
               './KJAX20150828_010610_V06.gz',
               './KJAX20150828_011028_V06.gz',
               './KJAX20150828_011506_V06.gz',
               './KJAX20150828_011930_V06.gz',
               './KJAX20150828_012400_V06.gz',
               './KJAX20150828_012827_V06.gz',
               './KJAX20150828_013324_V06.gz',
               './KJAX20150828_013757_V06.gz',
               './KJAX20150828_014231_V06.gz',
               './KJAX20150828_014659_V06.gz',
               './KJAX20150828_015129_V06.gz',
               './KJAX20150828_015603_V06.gz',
               './KJAX20150828_020017_V06.gz',
               './KJAX20150828_020431_V06.gz',
               './KJAX20150828_020836_V06.gz',
               './KJAX20150828_021255_V06.gz',
               './KJAX20150828_021701_V06.gz',
               './KJAX20150828_022127_V06.gz',
               './KJAX20150828_022557_V06.gz',
               './KJAX20150828_022952_V06.gz',
               './KJAX20150828_023346_V06.gz',
               './KJAX20150828_023738_V06.gz',
               './KJAX20150828_024129_V06.gz',
               './KJAX20150828_024524_V06.gz',
               './KJAX20150828_024920_V06.gz',
               './KJAX20150828_025313_V06.gz',
               './KJAX20150828_025835_V06.gz']

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
    ax.set_ylabel('North - South (km)')
    ax.set_title(radar_file[2:-7])
    save_file = './PNG/' + radar_file[2:-2] + 'png'
    fig.savefig(save_file, dpi=300, format='png')
    print("  - Done")