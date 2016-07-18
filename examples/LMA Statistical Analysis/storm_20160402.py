#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-04-02'

csv_all_flashes = path + '/Pandas/Storm_20160402_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20160402_pandas_all_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20160402_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20160402_pandas_big_source_count' \
                              '.csv'

dates = ['04/02/2016']

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis_20160402_0930-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_0940-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_0950-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1000-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1010-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1020-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1030-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1040-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1050-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1100-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1110-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1120-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1130-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1140-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1150-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1200-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1210-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1220-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1230-exported.csv',
                  path + '/xlma/ChargeAnalysis_20160402_1240-exported.csv']

    print("Reading all xlma files...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
    print("Saving xlma all to CSV...")
    storm_lma.save_to_csv(csv_all_flashes)

else:
    print("Loading all flashes from CSV...")
    storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

if not(os.path.isfile(csv_big_flashes)):
    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', csv_big_flashes)

    storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes],
                                               dates)

else:
    print("Loading the big flashes from CSV...")
    storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes],
                                               dates)

if not(os.path.isfile(csv_all_source_count)):
    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(csv_big_source_count)):
    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)