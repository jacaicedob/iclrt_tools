#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-03-04'

csv_all_flashes = path + '/Pandas/Storm_20160304_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20160304_pandas_all_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20160304_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20160304_pandas_big_source_count' \
                              '.csv'

dates = ['03/04/2016']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis_20160304_0540.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0550.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0600.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0610.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0620.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0630.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0640.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0650.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160304_0700.exported.csv']

    print("Reading all xlma files...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
    print("Saving xlma all to CSV...")
    storm_lma.save_to_csv(csv_all_flashes)

if not (os.path.isfile(csv_big_flashes)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', csv_big_flashes)
    storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes],
                                               dates)

if not (os.path.isfile(csv_all_source_count)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not (os.path.isfile(csv_big_source_count)):
    if storm_lma_big is None:
        print("Loading the big flashes from CSV...")
        storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes],
                                                   dates)

    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)

# import pandas as pd
# import datetime
# import iclrt_tools.lma.analysis.storm_analysis as st
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os
# import pickle

# # Operations to be performed on raw data
# sort_flashes_into_cells = False
# get_flash_numbers_from_lma = False
#
# path = '/home/jaime/Documents/ResearchTopics/Publications/'\
#        'LightningEvolution/Storm-03-04-2016/'

# # LOAD LMA DATA
# # Raw LMA files
# cell_1_lma_files = [path + 'LMA/ChargeAnalysis_Cell1_0540-exported.csv',
#                      path + 'LMA/ChargeAnalysis_Cell1_0550-exported.csv',
#                      path + 'LMA/ChargeAnalysis_Cell1_0600-exported.csv',
#                      path + 'LMA/ChargeAnalysis_Cell1_0610-exported.csv',
#                      path + 'LMA/ChargeAnalysis_Cell1_0620-exported.csv']
#
# cell_2_lma_files = [path + 'LMA/ChargeAnalysis_Cell2_0600-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0610-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0620-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0630-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0640-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0650-exported.csv',
#                     path + 'LMA/ChargeAnalysis_Cell2_0700-exported.csv']
#
# dates = ['03/04/2016']
#
# # Pickled files
# cell_1_lma_pickle = path + 'Statistical Analysis/cell_1_lma.p'
# cell_2_lma_pickle = path + 'Statistical Analysis/cell_2_lma.p'
#
# # Load Cell 1 LMA
# if not(os.path.isfile(cell_1_lma_pickle)):
#     storm_1_lma = st.StormLMA.from_lma_files(cell_1_lma_files, dates)
#     storm_1_lma.save_to_pickle(cell_1_lma_pickle)
# else:
#     storm_1_lma = st.StormLMA()
#     storm_1_lma.from_pickle(cell_1_lma_pickle)
#
# # Load Cell 1 LMA
# if not(os.path.isfile(cell_2_lma_pickle)):
#     storm_2_lma = st.StormLMA.from_lma_files(cell_2_lma_files, dates)
#     storm_2_lma.save_to_pickle(cell_2_lma_pickle)
# else:
#     storm_2_lma = st.StormLMA()
#     storm_2_lma.from_pickle(cell_2_lma_pickle)
#
# # LOAD .ODS DATA
# # Raw CSV files
# cell_1_ods_file = path + 'Cell1 Analysis 03042016.csv'
# cell_2_ods_file = path + 'Cell2 Analysis 03042016.csv'
#
# # Pickled files
# cell_1_ods_pickle = path + 'Statistical Analysis/cell_1_ods.p'
# cell_2_ods_pickle = path + 'Statistical Analysis/cell_2_ods.p'
#
# cell_1_ods_pickle_csv = path + 'Statistical Analysis/cell_1_ods.csv'
# cell_2_ods_pickle_csv = path + 'Statistical Analysis/cell_2_ods.csv'
#
# # Load Cell 1 ods
# if not(os.path.isfile(cell_1_ods_pickle)):
#     storm_1_ods = st.StormODS.from_ods_file(cell_1_ods_file)
# else:
#     storm_1_ods = st.StormODS()
#     storm_1_ods.from_pickle(cell_1_ods_pickle)
#
# # Load Cell 2 ods
# if not(os.path.isfile(cell_2_ods_pickle)):
#     storm_2_ods = st.StormODS.from_ods_file(cell_2_ods_file)
# else:
#     storm_2_ods = st.StormODS()
#     storm_2_ods.from_pickle(cell_2_ods_pickle)
#
# # Perform operations on raw data (if applicable)
# if get_flash_numbers_from_lma:
#     # Cell 1
#     data = st.StormLMA(storm_1_lma.filter_stations(6, inplace=False))
#     data.filter_chi_squared(5, inplace=True)
#     s = storm_1_ods.get_analyzed_flash_numbers(data, verbose=True)
#     storm_1_ods = st.StormODS(s)
#     storm_1_ods.save_to_pickle(cell_1_ods_pickle)
#     storm_1_ods.storm.to_csv(cell_1_ods_pickle_csv)
#
#     # Cell 2
#     data = st.StormLMA(storm_2_lma.filter_stations(6, inplace=False))
#     data.filter_chi_squared(5, inplace=True)
#     s = storm_2_ods.get_analyzed_flash_numbers(data, verbose=True)
#     storm_2_ods = st.StormODS(s)
#     storm_2_ods.save_to_pickle(cell_2_ods_pickle)
#     storm_2_ods.storm.to_csv(cell_2_ods_pickle_csv)
#
#
# cell_1_analyzer = st.Analysis(storm_1_lma, storm_1_ods)
# cell_2_analyzer = st.Analysis(storm_2_lma, storm_2_ods)
# st.Analysis.nice_plots()
#
# # # storm_2_lma.plot_charge_region(charge='positive')
# # # storm_2_lma.plot_charge_region(charge='negative')
# # # storm_2_lma.plot_all_charge_regions(show_plot=True)
# #
# # # ics = storm_1_ods.get_flash_type('IC')
# # # cgs = storm_1_ods.get_flash_type('-CG')
# # ics = storm_2_ods.get_flash_type('IC')
# # cgs = storm_2_ods.get_flash_type('-CG')
# #
# # # ic_series = ics['Initiation Height (km)']
# # # cg_series = cgs['Initiation Height (km)']
# # ic_series = ics['Area (km^2)']
# # cg_series = cgs['Area (km^2)']
# #
# # data_frame = pd.DataFrame({' ICs': ic_series, '-CGs': cg_series})
# # fig, ax = plt.subplots(1, 1, figsize=(12, 6))
# # data_frame.plot.hist(alpha=0.5, ax=ax)
# # # ax.set_title('Histogram of Initiation Heights for ICs and -CGs')
# # # ax.set_xlabel('Initiation Height (km)')
# # ax.set_title('Histogram of Flash Areas (from Plan View) for ICs and -CGs')
# # ax.set_xlabel(r'Flash Area (km$^2$)')
# # ax.legend()
# # plt.show()
# #
# #
# # # storm_1_ods.get_flash_rate(category='IC')
# # # storm_1_ods.get_flash_rate(category='CG')
# # # storm_1_lma.plot_all_charge_regions()
# # #
# # # storm_2_ods.get_flash_rate(category='IC')
# # # storm_2_ods.get_flash_rate(category='CG')
# # # storm_2_lma.plot_all_charge_regions(show_plot=True)
