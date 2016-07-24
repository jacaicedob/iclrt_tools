#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names containing all data
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-04-02'

csv_all_flashes = path + '/Pandas/Storm_20160402_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20160402_pandas_all_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20160402_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20160402_pandas_big_source_count' \
                              '.csv'

ods_file = path + '/ods/Cell 1 Analysis 04022016.csv'

lma_csv_big_matched_flashes = path + '/Pandas/Storm_20160402_pandas_big_matched_lma.csv'
ods_csv_big_matched_flashes = path + '/Pandas/Storm_20160402_pandas_big_matched_ods.csv'

csv_duplicate_flashes = path + \
                        '/Pandas/Storm_20160402_pandas_big_duplicates.csv'

dates = ['04/02/2016']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

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

if not (os.path.isfile(lma_csv_big_matched_flashes)) or \
   not (os.path.isfile(ods_csv_big_matched_flashes)) or \
   not (os.path.isfile(csv_duplicate_flashes)):
    print("Loading the big flashes from CSV...")
    # Read in the information
    storm_lma = st.StormLMA.from_lma_files([csv_big_flashes], dates)
    storm_ods = st.StormODS.from_ods_file(ods_file)

    print("Matching the LMA flashes to the ODS entries...")
    # Match the LMA flash numbers with the ODS entries
    result, dups = storm_ods.get_analyzed_flash_numbers(storm_lma,
                                                        verbose=True,
                                                        return_duplicates=True)
    # Get the matched DataFrames
    print("Getting the matches...")
    ods_matched = result[~st.pd.isnull(result['flash-number'])]
    numbers = ods_matched['flash-number'].unique()
    lma_matched = storm_lma.get_sources_from_flash_number(numbers)

    # Save to CSV
    print("Saving matches to CSV...")
    lma_matched.to_csv(lma_csv_big_matched_flashes, index=False)
    ods_matched.to_csv(ods_csv_big_matched_flashes, index=False)
    print("Saving the duplicate flash number list...")
    dups.to_csv(csv_duplicate_flashes)

