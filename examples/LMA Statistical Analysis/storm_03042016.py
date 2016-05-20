#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle

# Operations to be performed on raw data
sort_flashes_into_cells = False
get_flash_numbers_from_lma = True

path = '/home/jaime/Documents/ResearchTopics/Publications/'\
       'LightningEvolution/Storm-03-04-2016/'

# LOAD LMA DATA
# Raw LMA files
cell_1_lma_files = [path + 'LMA/ChargeAnalysis_Cell1_0540-exported.csv',
                     path + 'LMA/ChargeAnalysis_Cell1_0550-exported.csv',
                     path + 'LMA/ChargeAnalysis_Cell1_0600-exported.csv',
                     path + 'LMA/ChargeAnalysis_Cell1_0610-exported.csv',
                     path + 'LMA/ChargeAnalysis_Cell1_0620-exported.csv']

cell_2_lma_files = [path + 'LMA/ChargeAnalysis_Cell2_0600-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0610-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0620-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0630-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0640-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0650-exported.csv',
                    path + 'LMA/ChargeAnalysis_Cell2_0700-exported.csv']

dates = ['03/04/2016']

# Pickled files
cell_1_pickle = path + 'Statistical Analysis/cell_1_lma.p'
cell_2_pickle = path + 'Statistical Analysis/cell_2_lma.p'

# Load Cell 1 LMA
if not(os.path.isfile(cell_1_pickle)):
    storm_lma_1 = st.StormLMA.from_lma_files(cell_1_lma_files, dates)
else:
    storm_lma_1 = st.StormLMA()
    storm_lma_1.from_pickle(cell_1_pickle)

# Load Cell 1 LMA
if not(os.path.isfile(cell_2_pickle)):
    storm_lma_2 = st.StormLMA.from_lma_files(cell_2_lma_files, dates)
else:
    storm_lma_2 = st.StormLMA()
    storm_lma_2.from_pickle(cell_2_pickle)

# LOAD .ODS DATA
# Raw CSV files
cell_1_ods_file = path + 'Cell1 Analysis 03042016.csv'
cell_2_ods_file = path + 'Cell2 Analysis 03042016.csv'

# Pickled files
cell_1_ods_pickle = path + 'Statistical Analysis/cell_1_ods.p'
cell_2_ods_pickle = path + 'Statistical Analysis/cell_2_ods.p'

# Load Cell 1 ods
if not(os.path.isfile(cell_1_ods_pickle)):
    storm_ods_1 = st.StormODS.from_ods_file(cell_1_ods_file)
else:
    storm_ods_1 = st.StormODS()
    storm_ods_1.from_pickle(cell_1_ods_pickle)

# Load Cell 2 ods
if not(os.path.isfile(cell_2_ods_pickle)):
    storm_ods_2 = st.StormODS.from_ods_file(cell_2_ods_file)
else:
    storm_ods_2 = st.StormODS()
    storm_ods_2.from_pickle(cell_2_ods_pickle)

# Perform operations on raw data (if applicable)
if get_flash_numbers_from_lma:
    # Cell 1
    data = st.StormLMA(storm_lma_1.filter_stations(6, inplace=False))
    data.filter_chi_squared(5, inplace=True)
    s = storm_ods_1.get_analyzed_flash_numbers(data, verbose=True)
    storm_ods_1 = st.StormODS(s)

    # Cell 2
    data = st.StormLMA(storm_lma_2.filter_stations(6, inplace=False))
    data.filter_chi_squared(5, inplace=True)
    s = storm_ods_2.get_analyzed_flash_numbers(data, verbose=True)
    storm_ods_2 = st.StormODS(s)


# st.Analysis.nice_plots()
#
# # storm_lma_2.plot_charge_region(charge='positive')
# # storm_lma_2.plot_charge_region(charge='negative')
# # storm_lma_2.plot_all_charge_regions(show_plot=True)
#
# # ics = storm_ods_1.get_flash_type('IC')
# # cgs = storm_ods_1.get_flash_type('-CG')
# ics = storm_ods_2.get_flash_type('IC')
# cgs = storm_ods_2.get_flash_type('-CG')
#
# # ic_series = ics['Initiation Height (km)']
# # cg_series = cgs['Initiation Height (km)']
# ic_series = ics['Area (km^2)']
# cg_series = cgs['Area (km^2)']
#
# data_frame = pd.DataFrame({' ICs': ic_series, '-CGs': cg_series})
# fig, ax = plt.subplots(1, 1, figsize=(12, 6))
# data_frame.plot.hist(alpha=0.5, ax=ax)
# # ax.set_title('Histogram of Initiation Heights for ICs and -CGs')
# # ax.set_xlabel('Initiation Height (km)')
# ax.set_title('Histogram of Flash Areas (from Plan View) for ICs and -CGs')
# ax.set_xlabel(r'Flash Area (km$^2$)')
# ax.legend()
# plt.show()
#
#
# # storm_ods_1.get_flash_rate(category='IC')
# # storm_ods_1.get_flash_rate(category='CG')
# # storm_lma_1.plot_all_charge_regions()
# #
# # storm_ods_2.get_flash_rate(category='IC')
# # storm_ods_2.get_flash_rate(category='CG')
# # storm_lma_2.plot_all_charge_regions(show_plot=True)
