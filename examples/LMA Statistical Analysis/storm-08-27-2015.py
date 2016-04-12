#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# File names for first and second part of storm analysis
file1 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-1of2-exported.csv'
file2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-2of2-exported.csv'

dates = ['08/27/2015', '08/28/2015']

file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA Analysis 08272015.csv'

storm_lma = st.StormLMA.from_lma_files([file1, file2], dates)
storm_ods = st.StormODS.from_ods_file(file_name)
sns.set_context('talk', font_scale=2.0)

# Get flash numbers for all ODS flashes
# results = storm_lma.get_analyzed_flash_numbers(storm_ods)

storm_lma.plot_charge_region(charge='positive')
storm_lma.plot_charge_region(charge='negative')
storm_lma.plot_all_charge_regions(show_plot=True)

for t in storm_ods.storm['Type'].unique():
    storm_ods.analyze_flash_areas(flash_type=t)

for t in storm_ods.storm['Type'].unique():
    storm_ods.analyze_initiation_heights(flash_type=t)

# ics = storm_ods.get_flash_type('IC')
# cgs = storm_ods.get_flash_type('-CG')
#
# # ic_series = ics['Initiation Height (km)']
# # cg_series = cgs['Initiation Height (km)']
# ic_series = ics['Area (km^2)']
# cg_series = cgs['Area (km^2)']
#
# data_frame = pd.DataFrame({' ICs': ic_series, 'CGs': cg_series})
# fig, ax = plt.subplots(1, 1, figsize=(12, 6))
# data_frame.plot.hist(alpha=0.5, ax=ax)
# # ax.set_title('Histogram of initiation heights for ICs and -CGs')
# # ax.set_xlabel('Initiation Height (km)')
# ax.set_title('Histogram of flash areas for ICs and -CGs')
# ax.set_xlabel(r'Flash Area (km$^2$)')
# ax.legend()
# plt.show()


# storm_lma.plot_charge_region(charge='positive', show_plot=True)
# storm_lma.plot_charge_region(charge='negative', show_plot=True)
# storm_lma.plot_all_charge_regions(show_plot=True)

# storm_lma.get_storm_summary(charge='positive')
# storm_lma.get_storm_summary(charge='negative')
# storm_lma.get_storm_summary(charge='other')
# storm_ods.get_storm_summary(flash_types=['IC'])

# storm_ods.get_flash_rate(category='CG')
# storm_ods.get_flash_rate(category='IC')
# storm_lma.plot_interval(path='/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/Figures/Statistical Analysis/')

# storm_lma.measure_flash_area('/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/Statistical Analysis/storm-08-27-2015_flash_areas.csv')