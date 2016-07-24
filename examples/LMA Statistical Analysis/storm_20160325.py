#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-03-25'

csv_all_flashes = path + '/Pandas/Storm_20160325_pandas_all_lma.csv'
csv_all_source_count = path + \
                       '/Pandas/Storm_20160325_pandas_all_lma_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20160325_pandas_big_lma.csv'
csv_big_source_count = path + \
                       '/Pandas/Storm_20160325_pandas_big_lma_source_count' \
                              '.csv'

ods_file = [path + '/ods/Cell 1 Analysis 03252016.csv',
            path + '/ods/Cell 2 Analysis 03252016.csv']

lma_csv_big_matched_flashes = path + '/Pandas/' \
                                     'Storm_20160325_pandas_big_matched_lma.csv'
ods_csv_big_matched_flashes = path + '/Pandas/' \
                                     'Storm_20160325_pandas_big_matched_ods.csv'
ods_csv_big_matched_flashes_2 = path + '/Pandas/' \
                                       'Storm_20160325_pandas_big_matched_ods_2.csv'

csv_duplicate_flashes = path + \
                        '/Pandas/Storm_20160325_pandas_big_matched_duplicates.csv'

dates = ['03/25/2016']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis_20160325_0200.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0210.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0220.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0230.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0240.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0250.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0300.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0310.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0320.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0330.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0340.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0350.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0400.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0410.exported.csv',
                  path + '/xlma/ChargeAnalysis_20160325_0420.exported.csv']

    print("Reading all xlma files...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
    print("Converting coordinates to meters...")
    storm_lma.convert_latlon_to_m(verbose=True)
    print("Saving xlma all to CSV...")
    storm_lma.save_to_csv(csv_all_flashes)

if not (os.path.isfile(csv_big_flashes)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', csv_big_flashes)

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
   not (os.path.isfile(ods_csv_big_matched_flashes_2)) or \
   not (os.path.isfile(csv_duplicate_flashes)):

    print("Loading the big flashes from CSV...")
    # Read in the information
    storm_lma = st.StormLMA.from_lma_files([csv_big_flashes], dates)
    storm_ods = st.StormODS.from_ods_file(ods_file[0])
    storm_ods_2 = st.StormODS.from_ods_file(ods_file[1])

    print("Matching the LMA flashes to the ODS entries...")
    # Match the LMA flash numbers with the ODS entries
    result, dups = storm_ods.get_analyzed_flash_numbers(storm_lma,
                                                        verbose=True,
                                                        return_duplicates=True)
    result_2, dups_2 = storm_ods_2.get_analyzed_flash_numbers(storm_lma,
                                                              verbose=True,
                                                              return_duplicates=True)

    # Get the matched DataFrames
    print("Getting the matches...")
    ods_matched = result[~st.pd.isnull(result['flash-number'])]
    numbers = ods_matched['flash-number'].unique()

    ods_matched_2 = result_2[~st.pd.isnull(result_2['flash-number'])]
    numbers_2 = ods_matched_2['flash-number'].unique()

    numbers = list(numbers) + list(numbers_2)
    print("Number of matched flash numbers:", len(numbers))

    lma_matched = storm_lma.get_sources_from_flash_number(numbers)

    dups = st.pd.concat([dups, dups_2], ignore_index=True)

    # Save to CSV
    print("Saving matches to CSV...")
    print("  Saving LMA...")
    lma_matched.to_csv(lma_csv_big_matched_flashes, index=False)
    print("  Saving ODS...")
    ods_matched.to_csv(ods_csv_big_matched_flashes, index=False)
    ods_matched_2.to_csv(ods_csv_big_matched_flashes_2, index=False)
    print("Saving the duplicate flash number list...")
    dups.to_csv(csv_duplicate_flashes)
