#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-02-24'

csv_all_flashes = path + '/Pandas/Storm_20160224_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20160224_pandas_all_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20160224_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20160224_pandas_big_source_count' \
                              '.csv'

dates = ['02/24/2016']

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis_20160224_1120-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1130-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1140-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1150-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1200-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1210-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160224_1220-exported.csv']

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

# storm_ods = st.Storm.from_ods_file(file_name)
#
# storm_ods.get_flash_rate(category='IC')
# storm_lma.plot_charge_region(show_plot=True)
# storm_lma.plot_all_charge_regions(show_plot=True)
# storm_lma.analyze_subset('2016-02-24 11:25:00.0', '2016-02-24 13:30:00.0', plot=True)
