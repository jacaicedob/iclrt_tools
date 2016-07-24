#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names containing all data
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2012-07-17'

csv_all_flashes = path + '/Pandas/Storm_20120717_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20120717_pandas_all_source_count' \
                              '.csv'
csv_big_flashes = path + '/Pandas/Storm_20120717_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20120717_pandas_big_source_count' \
                              '.csv'

ods_file = [path + '/ods/Cell1 Analysis 07172012.csv',
            path + '/ods/Cell2 Analysis 07172012.csv']

lma_csv_big_matched_flashes = path + '/Pandas/' \
                              'Storm_20120717_pandas_big_matched_lma.csv'
ods_csv_big_matched_flashes = path + '/Pandas/' \
                              'Storm_20120717_pandas_big_matched_ods.csv'
ods_csv_big_matched_flashes_2 = path + '/Pandas/' \
                                'Storm_20120717_pandas_big_matched_ods_2.csv'

csv_duplicate_flashes = path + \
                        '/Pandas/Storm_20120717_pandas_big_duplicates.csv'

dates = ['07/17/2012']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis_20120717_1900.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_1910.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_1920.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_1930.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_1940.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_1950.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2000.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2010.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2020.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2030.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2040.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2050.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2100.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2110.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2120.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2130.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2140.exported.csv',
                  path + '/xlma/ChargeAnalysis_20120717_2150.exported.csv']

    print("Reading all xlma files...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
    print("Converting coordinates to meters...")
    storm_lma.convert_latlon_to_m(verbose=True)
    print("Saving xlma all to CSV...")
    storm_lma.save_to_csv(csv_all_flashes)

if not(os.path.isfile(csv_big_flashes)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', csv_big_flashes)

    storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes],
                                               dates)

if not(os.path.isfile(csv_all_source_count)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes], dates)

    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(csv_big_source_count)):
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


# # File names and analysis flags for .ods files
# sort_flashes = False
# get_flash_numbers = False
#
# sorted_file_name = path + '/Statistical Analysis/07172012-Sorted_into_cells'
# sorted_pickle = sorted_file_name + '.p'
# sorted_csv = sorted_file_name + '.csv'
# flash_numbers_pickle = path + \
#                        '/Statistical Analysis/07172012_ods_flash-numbers.p'
# flash_numbers_csv = path + \
#                     '/Statistical Analysis/07172012_ods_flash-numbers.csv'
# original_csv = path + '/Cell 1 LMA Analysis 07172012.ods'
#
# file_name = sorted_csv
# pickle_file = sorted_pickle
#
# # Load the most analyzed file first if it exists. If no analyzed file exists
# # set the flags to do the analysis and save the analyzed data for future runs.
#
# if not(os.path.isfile(pickle_file)):
#     if not (os.path.isfile(file_name)):
#         sort_flashes = True
#         pickle_file = flash_numbers_pickle
#         file_name = flash_numbers_csv
#
#         if not(os.path.isfile(pickle_file)):
#             if not(os.path.isfile(file_name)):
#                 get_flash_numbers = True
#                 storm_ods = st.StormODS.from_ods_file(original_csv)
#
#             else:
#                 storm_ods = st.StormODS.from_ods_file(file_name)
#
#         else:
#             storm_ods = st.StormODS()
#             storm_ods.from_pickle(pickle_file)
#     else:
#         storm_ods = st.StormODS.from_ods_file(file_name)
#
# else:
#     storm_ods = st.StormODS()
#     storm_ods.from_pickle(pickle_file)
#
# if get_flash_numbers:
#     s = storm_ods.get_analyzed_flash_numbers(storm_lma, verbose=True)
#     s.save_to_pickle(flash_numbers_pickle)
#     s.to_csv(flash_numbers_csv)
#     storm_ods = s
#
# # Cell definitions
# # Entire storm
# cell_times = [datetime.datetime(2012, 7, 17, 18, 17, 0),
#               datetime.datetime(2012, 7, 17, 18, 22, 0),
#               datetime.datetime(2012, 7, 17, 18, 27, 0),
#               datetime.datetime(2012, 7, 17, 18, 31, 0),
#               datetime.datetime(2012, 7, 17, 18, 36, 0),
#               datetime.datetime(2012, 7, 17, 18, 41, 0),
#               datetime.datetime(2012, 7, 17, 18, 45, 0),
#               datetime.datetime(2012, 7, 17, 18, 50, 0),
#               datetime.datetime(2012, 7, 17, 18, 55, 0),
#               datetime.datetime(2012, 7, 17, 19, 0, 0),
#               datetime.datetime(2012, 7, 17, 19, 4, 0),
#               datetime.datetime(2012, 7, 17, 19, 9, 0),
#               datetime.datetime(2012, 7, 17, 19, 14, 0),
#               datetime.datetime(2012, 7, 17, 19, 18, 0),
#               datetime.datetime(2012, 7, 17, 19, 23, 0),
#               datetime.datetime(2012, 7, 17, 19, 28, 0),
#               datetime.datetime(2012, 7, 17, 19, 32, 0),
#               datetime.datetime(2012, 7, 17, 19, 37, 0),
#               datetime.datetime(2012, 7, 17, 19, 42, 0),
#               datetime.datetime(2012, 7, 17, 19, 47, 0),
#               datetime.datetime(2012, 7, 17, 19, 51, 0),
#               datetime.datetime(2012, 7, 17, 19, 56, 0),
#               datetime.datetime(2012, 7, 17, 20, 1, 0),
#               datetime.datetime(2012, 7, 17, 20, 5, 0),
#               datetime.datetime(2012, 7, 17, 20, 10, 0),
#               datetime.datetime(2012, 7, 17, 20, 15, 0),
#               datetime.datetime(2012, 7, 17, 20, 20, 0),
#               datetime.datetime(2012, 7, 17, 20, 24, 0),
#               datetime.datetime(2012, 7, 17, 20, 29, 0),
#               datetime.datetime(2012, 7, 17, 20, 34, 0),
#               datetime.datetime(2012, 7, 17, 20, 39, 0),
#               datetime.datetime(2012, 7, 17, 20, 44, 0),
#               datetime.datetime(2012, 7, 17, 20, 48, 0),
#               datetime.datetime(2012, 7, 17, 20, 53, 0),
#               datetime.datetime(2012, 7, 17, 20, 58, 0),
#               datetime.datetime(2012, 7, 17, 21, 2, 0),
#               datetime.datetime(2012, 7, 17, 21, 7, 0),
#               datetime.datetime(2012, 7, 17, 21, 11, 0),
#               datetime.datetime(2012, 7, 17, 21, 16, 0),
#               datetime.datetime(2012, 7, 17, 21, 21, 0),
#               datetime.datetime(2012, 7, 17, 21, 26, 0),
#               datetime.datetime(2012, 7, 17, 21, 30, 0),
#               datetime.datetime(2012, 7, 17, 21, 35, 0),
#               datetime.datetime(2012, 7, 17, 21, 40, 0),
#               datetime.datetime(2012, 7, 17, 21, 44, 0),
#               datetime.datetime(2012, 7, 17, 21, 49, 0),
#               datetime.datetime(2012, 7, 17, 21, 54, 0),
#               datetime.datetime(2012, 7, 17, 21, 59, 0)]
#
# cell_xlims = [(-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3)]
#
# cell_ylims = [(-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3),
#               (-50e3, 50e3)]
#
# # Define Cell 1
# cell_1_times = []
#
# cell_1_xlims = []
#
# cell_1_ylims = []
#
# # # Combine definitions into a Cell object
# # cells = dict()
# # cells['Cell 1'] = st.Cell('Cell 1', cell_1_times, cell_1_xlims, cell_1_ylims)
# # cells['Cell 2'] = st.Cell('Cell 2', cell_2_times, cell_2_xlims, cell_2_ylims)
# # cells['Cell 3'] = st.Cell('Cell 3', cell_3_times, cell_3_xlims, cell_3_ylims)
# # cells['Cell 1-2'] = st.Cell('Cell 1-2', cell_12_times, cell_12_xlims, cell_12_ylims)
# #
# # cells = dict()
# # cells['All'] = st.Cell('All', cell_times, cell_xlims, cell_ylims)
# #
# # # Create the Analsysis object
# # analyzer = st.Analysis(storm_lma, storm_ods, cells)
# #
# # # If the flashes have not been sorted into each cell, do so.
# # if sort_flashes:
# #     analyzer.sort_into_cells(sorted_file_name, 15)
# #
# # # Get the StormLMA and StormODS objects from sorted data.
# # for cell in cells:
# #     cells[cell].set_ods(analyzer.ods.get_cell_ods(cell))
# #     cells[cell].set_lma(analyzer.lma.get_lma_from_ods(cells[cell].ods))
# #     cells[cell].lma.storm.sort_index(inplace=True)

