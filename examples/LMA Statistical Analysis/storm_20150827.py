#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2015-08-27'

csv_all_flashes = path + '/Pandas/Storm_20150827_pandas_all.csv'
csv_all_flashes_2 = path + '/Pandas/Storm_20150828_pandas_all.csv'
csv_all_source_count = path + '/Pandas/Storm_20150827_pandas_all_source_count' \
                              '.csv'

csv_big_flashes = path + '/Pandas/Storm_20150827_pandas_big.csv'
csv_big_flashes_2 = path + '/Pandas/Storm_20150828_pandas_big.csv'
csv_big_source_count = path + '/Pandas/Storm_20150827_pandas_big_source_count' \
                              '.csv'

ods_file = path + '/ods/LMA Analysis 08272015.csv'

lma_csv_big_matched_flashes = path + \
                              '/Pandas/Storm_20150827_pandas_big_matched_lma' \
                              '.csv'
ods_csv_big_matched_flashes = path + \
                              '/Pandas/Storm_20150827_pandas_big_matched_ods' \
                              '.csv'

csv_duplicate_flashes = path + \
                        '/Pandas/Storm_20150827_pandas_big_duplicates.csv'

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None
storm_lma_2 = None
storm_lma_big_2 = None

if not(os.path.isfile(csv_all_flashes)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis-1of2-exported.csv']

    print("Reading all xlma files 08/27/2015...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, ['08/27/2015'])
    print("Converting coordinates to meters...")
    storm_lma.convert_latlon_to_m(verbose=True)
    print("Saving xlma all to CSV 08/27/2015...")
    storm_lma.save_to_csv(csv_all_flashes)

if not(os.path.isfile(csv_all_flashes_2)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis-2of2-exported.csv']

    print("Reading all xlma files 08/28/2015...")
    storm_lma_2 = st.StormLMA.from_lma_files(xlma_files, ['08/28/2015'])
    print("Converting coordinates to meters...")
    storm_lma_2.convert_latlon_to_m(verbose=True)
    print("Saving xlma all to CSV 08/28/2015...")
    storm_lma_2.save_to_csv(csv_all_flashes_2)

if not(os.path.isfile(csv_big_flashes)):
    if storm_lma is None:
        print("Loading all flashes from CSV 08/27/2015...")
        # Read in the information
        storm_lma = st.StormLMA.from_lma_files([csv_all_flashes],
                                               ['08/27/2015'])

    print("Saving big flashes to CSV  08/27/2015...")
    storm_lma.save_flashes_by_size('big', csv_big_flashes)

if not(os.path.isfile(csv_big_flashes_2)):
    if storm_lma_2 is None:
        print("Loading all flashes from CSV 08/28/2015...")
        # Read in the information
        storm_lma_2 = st.StormLMA.from_lma_files([csv_all_flashes_2],
                                                 ['08/28/2015'])

    print("Saving big flashes to CSV  08/28/2015...")
    storm_lma_2.save_flashes_by_size('big', csv_big_flashes_2)

if not(os.path.isfile(csv_all_source_count)):
    print("Loading all flashes from CSV...")
    storm_lma = st.StormLMA.from_lma_files([csv_all_flashes, csv_all_flashes_2],
                                           ['08/27/2015', '08/28/2015'])
    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(csv_big_source_count)):
    print("Loading the big flashes from CSV...")
    storm_lma_big = st.StormLMA.from_lma_files([csv_big_flashes,
                                                csv_big_flashes_2],
                                               ['08/27/2015', '08/28/2015'])
    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)

if not (os.path.isfile(lma_csv_big_matched_flashes)) or \
   not (os.path.isfile(ods_csv_big_matched_flashes)) or \
   not (os.path.isfile(csv_duplicate_flashes)):
    print("Loading the big flashes from CSV...")
    # Read in the information
    storm_lma = st.StormLMA.from_lma_files([csv_big_flashes,
                                            csv_big_flashes_2],
                                           ['08/27/2015', '08/28/2015'])
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
    print("Number of matched flash numbers:", len(numbers))

    lma_matched = storm_lma.get_sources_from_flash_number(numbers)

    # Save to CSV
    print("Saving matches to CSV...")
    print("  Saving LMA...")
    lma_matched.to_csv(lma_csv_big_matched_flashes, index=False)
    print("  Saving ODS...")
    ods_matched.to_csv(ods_csv_big_matched_flashes, index=False)

    print("Saving the duplicate flash number list...")
    dups.to_csv(csv_duplicate_flashes)

# # File names and analysis flags for .ods files
# sort_flashes = False
# get_flash_numbers = False
#
# sorted_file_name = path + '/Statistical Analysis/08272015-Sorted_into_cells'
# sorted_pickle = sorted_file_name + '.p'
# sorted_csv = sorted_file_name + '.csv'
# flash_numbers_pickle = path + \
#                        '/Statistical Analysis/08272015_ods_flash-numbers.p'
# flash_numbers_csv = path + \
#                     '/Statistical Analysis/08272015_ods_flash-numbers.csv'
# original_csv = path + '/LMA Analysis 08272015.csv'
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
#     to_sort = st.StormLMA(storm_lma.filter_stations(7, inplace=False))
#     to_sort.filter_chi_squared(1, inplace=True)
#     s = storm_ods.get_analyzed_flash_numbers(to_sort, verbose=True)
#     s.save_to_pickle(flash_numbers_pickle)
#     s.to_csv(flash_numbers_csv)
#     storm_ods = s
#
# # Cell definitions
# # Entire storm
# cell_times = [datetime.datetime(2015, 8, 27, 22, 36, 0),
#               datetime.datetime(2015, 8, 27, 22, 40, 0),
#               datetime.datetime(2015, 8, 27, 22, 44, 0),
#               datetime.datetime(2015, 8, 27, 22, 48, 0),
#               datetime.datetime(2015, 8, 27, 22, 52, 0),
#               datetime.datetime(2015, 8, 27, 22, 56, 0),
#               datetime.datetime(2015, 8, 27, 23, 0, 0),
#               datetime.datetime(2015, 8, 27, 23, 4, 0),
#               datetime.datetime(2015, 8, 27, 23, 8, 0),
#               datetime.datetime(2015, 8, 27, 23, 13, 0),
#               datetime.datetime(2015, 8, 27, 23, 17, 0),
#               datetime.datetime(2015, 8, 27, 23, 21, 0),
#               datetime.datetime(2015, 8, 27, 23, 26, 0),
#               datetime.datetime(2015, 8, 27, 23, 30, 0),
#               datetime.datetime(2015, 8, 27, 23, 34, 0),
#               datetime.datetime(2015, 8, 27, 23, 38, 0),
#               datetime.datetime(2015, 8, 27, 23, 43, 0),
#               datetime.datetime(2015, 8, 27, 23, 47, 0),
#               datetime.datetime(2015, 8, 27, 23, 51, 0),
#               datetime.datetime(2015, 8, 27, 23, 56, 0),
#               datetime.datetime(2015, 8, 28, 0, 0, 0),
#               datetime.datetime(2015, 8, 28, 0, 5, 0),
#               datetime.datetime(2015, 8, 28, 0, 9, 0),
#               datetime.datetime(2015, 8, 28, 0, 14, 0),
#               datetime.datetime(2015, 8, 28, 0, 19, 0),
#               datetime.datetime(2015, 8, 28, 0, 23, 0),
#               datetime.datetime(2015, 8, 28, 0, 28, 0),
#               datetime.datetime(2015, 8, 28, 0, 33, 0)]
#
# cell_xlims = [(-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3)]
#
# cell_ylims = [(-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3),
#               (-20e3, 20e3)]
#
# # Define Cell 1
# cell_1_times = [datetime.datetime(2015, 8, 27, 22, 36, 0),
#                 datetime.datetime(2015, 8, 27, 22, 40, 0),
#                 datetime.datetime(2015, 8, 27, 22, 44, 0),
#                 datetime.datetime(2015, 8, 27, 22, 48, 0),
#                 datetime.datetime(2015, 8, 27, 22, 52, 0),
#                 datetime.datetime(2015, 8, 27, 22, 56, 0),
#                 datetime.datetime(2015, 8, 27, 23, 0, 0),
#                 datetime.datetime(2015, 8, 27, 23, 4, 0),
#                 datetime.datetime(2015, 8, 27, 23, 8, 0),
#                 datetime.datetime(2015, 8, 27, 23, 13, 0),
#                 datetime.datetime(2015, 8, 27, 23, 17, 0),
#                 datetime.datetime(2015, 8, 27, 23, 21, 0),
#                 datetime.datetime(2015, 8, 27, 23, 26, 0),
#                 datetime.datetime(2015, 8, 27, 23, 30, 0),
#                 datetime.datetime(2015, 8, 27, 23, 34, 0),
#                 datetime.datetime(2015, 8, 27, 23, 38, 0),
#                 datetime.datetime(2015, 8, 27, 23, 43, 0),
#                 datetime.datetime(2015, 8, 27, 23, 47, 0),
#                 datetime.datetime(2015, 8, 27, 23, 51, 0),
#                 datetime.datetime(2015, 8, 27, 23, 51, 0)]
#
#
# cell_1_xlims = [(-10e3, 10e3),
#                 (-10e3, 10e3),
#                 (-10e3, 8e3),
#                 (-15e3, 5e3),
#                 (-13e3, 8e3),
#                 (-13e3, 5e3),
#                 (-15e3, 5e3),
#                 (-15e3, 8e3),
#                 (-15e3, 5e3),
#                 (-15e3, 5e3),
#                 (-17e3, 8e3),
#                 (-17e3, 8e3),
#                 (-15e3, 8e3),
#                 (-17e3, 9e3),
#                 (-17e3, 5e3),
#                 (-17e3, 4e3),
#                 (-20e3, 7e3),
#                 (-20e3, 7e3),
#                 (-20e3, 10e3),
#                 (-20e3, -10.1e3)]
#
# cell_1_ylims = [(-5e3, 5e3),
#                 (-5e3, 8e3),
#                 (-5e3, 8e3),
#                 (-5e3, 8e3),
#                 (-5e3, 8e3),
#                 (-5e3, 8e3),
#                 (-5e3, 10e3),
#                 (-5e3, 10e3),
#                 (-10e3, 15e3),
#                 (-11e3, 18e3),
#                 (-13e3, 18e3),
#                 (-13e3, 18e3),
#                 (-11e3, 20e3),
#                 (-11e3, 20e3),
#                 (-9.9e3, 20e3),
#                 (-9.9e3, 5e3),
#                 (-9.9e3, 5e3),
#                 (-7.9e3, 7e3),
#                 (-8.9e3, 8e3),
#                 (-20e3, -8.9e3)]
#
# # Define Cell 1-2 (merger between cells 1 and 2)
# cell_12_times = [datetime.datetime(2015, 8, 27, 23, 56, 0),
#                  datetime.datetime(2015, 8, 28, 0, 0, 0),
#                  datetime.datetime(2015, 8, 28, 0, 0, 0),
#                  datetime.datetime(2015, 8, 28, 0, 5, 0),
#                  datetime.datetime(2015, 8, 28, 0, 5, 0),
#                  datetime.datetime(2015, 8, 28, 0, 5, 0),
#                  datetime.datetime(2015, 8, 28, 0, 9, 0),
#                  datetime.datetime(2015, 8, 28, 0, 9, 0),
#                  datetime.datetime(2015, 8, 28, 0, 9, 0),
#                  datetime.datetime(2015, 8, 28, 0, 14, 0),
#                  datetime.datetime(2015, 8, 28, 0, 14, 0),
#                  datetime.datetime(2015, 8, 28, 0, 14, 0),
#                  datetime.datetime(2015, 8, 28, 0, 19, 0),
#                  datetime.datetime(2015, 8, 28, 0, 19, 0),
#                  datetime.datetime(2015, 8, 28, 0, 23, 0),
#                  datetime.datetime(2015, 8, 28, 0, 23, 0),
#                  datetime.datetime(2015, 8, 28, 0, 28, 0)]
#
# cell_12_xlims = [(-20e3, 5e3),
#                  (-20e3, 9e3),
#                  (-6e3, 9e3),
#                  (-20e3, 9e3),
#                  (-12e3, 9e3),
#                  (-5e3, 9e3),
#                  (-20e3, 7e3),
#                  (-10e3, 73),
#                  (-7e3, 7e3),
#                  (-20e3, 7e3),
#                  (-10e3, 7e3),
#                  (-5e3, 7e3),
#                  (-20e3, 8e3),
#                  (-7e3, 8e3),
#                  (-20e3, 8e3),
#                  (-5e3, 8e3),
#                  (-20e3, 8e3)]
#
# cell_12_ylims = [(-17e3, 7.9e3),
#                  (-15e3, 7.9e3),
#                  (7.9e3, 20e3),
#                  (-13e3, 2e3),
#                  (2.1e3, 7e3),
#                  (7.1e3, 20e3),
#                  (-14e3, 3e3),
#                  (3.1e3, 9e3),
#                  (9.1e3, 20e3),
#                  (-14e3, 3e3),
#                  (3.1e3, 10e3),
#                  (10.1e3, 20e3),
#                  (-15e3, 5e3),
#                  (5.1e3, 20e3),
#                  (-15e3, 5e3),
#                  (5.1e3, 20e3),
#                  (-15e3, 5e3)]
#
# # Define Cell 2
#
# cell_2_times = [datetime.datetime(2015, 8, 27, 23, 17, 0),
#                 datetime.datetime(2015, 8, 27, 23, 21, 0),
#                 datetime.datetime(2015, 8, 27, 23, 26, 0),
#                 datetime.datetime(2015, 8, 27, 23, 30, 0),
#                 datetime.datetime(2015, 8, 27, 23, 34, 0),
#                 datetime.datetime(2015, 8, 27, 23, 38, 0),
#                 datetime.datetime(2015, 8, 27, 23, 43, 0),
#                 datetime.datetime(2015, 8, 27, 23, 47, 0),
#                 datetime.datetime(2015, 8, 27, 23, 51, 0)]
#
# cell_2_xlims = [(-5e3, 17e3),
#                 (-5e3, 19e3),
#                 (-5e3, 19e3),
#                 (-10e3, 20e3),
#                 (-10e3, 10e3),
#                 (-10e3, 8e3),
#                 (-12e3, 8e3),
#                 (-10e3, 7e3),
#                 (-10e3, 5e3)]
#
# cell_2_ylims = [(-20e3, -15e3),
#                 (-20e3, -13e3),
#                 (-20e3, -13e3),
#                 (-20e3, -13e3),
#                 (-20e3, -10e3),
#                 (-20e3, -10e3),
#                 (-20e3, -10e3),
#                 (-20e3, -8e3),
#                 (-18e3, -9e3)]
#
# # Define Cell 3
#
# cell_3_times = [datetime.datetime(2015, 8, 27, 23, 38, 0),
#                 datetime.datetime(2015, 8, 27, 23, 43, 0),
#                 datetime.datetime(2015, 8, 27, 23, 47, 0),
#                 datetime.datetime(2015, 8, 27, 23, 51, 0),
#                 datetime.datetime(2015, 8, 27, 23, 56, 0),
#                 datetime.datetime(2015, 8, 28, 0, 0, 0),
#                 datetime.datetime(2015, 8, 28, 0, 5, 0),
#                 datetime.datetime(2015, 8, 28, 0, 5, 0),
#                 datetime.datetime(2015, 8, 28, 0, 9, 0),
#                 datetime.datetime(2015, 8, 28, 0, 9, 0),
#                 datetime.datetime(2015, 8, 28, 0, 14, 0),
#                 datetime.datetime(2015, 8, 28, 0, 14, 0),
#                 datetime.datetime(2015, 8, 28, 0, 19, 0),
#                 datetime.datetime(2015, 8, 28, 0, 23, 0),
#                 datetime.datetime(2015, 8, 28, 0, 28, 0),
#                 datetime.datetime(2015, 8, 28, 0, 33, 0)]
#
# cell_3_xlims = [(-20e3, 20e3),
#                 (-20e3, 20e3),
#                 (-20e3, 20e3),
#                 (-20e3, 20e3),
#                 (-20e3, 20e3),
#                 (-20e3, -7e3),
#                 (-20e3, -12.1e3),
#                 (-12.1e3, -5.1e3),
#                 (-20e3, -10.1e3),
#                 (-10.1e3, -7.1),
#                 (-20e3, -10.1e3),
#                 (-10e3, -5.1e3),
#                 (-20e3, -7.1e3),
#                 (-20e3, -5.1e3),
#                 (-20e3, -5e3),
#                 (-20e3, -5e3)]
#
# cell_3_ylims = [(5.1e3, 20e3),
#                 (5.1e3, 20e3),
#                 (7.1e3, 20e3),
#                 (8.1e3, 20e3),
#                 (8e3, 20e3),
#                 (8.0e3, 20e3),
#                 (2.1e3, 20e3),
#                 (7.1e3, 20e3),
#                 (3.1e3, 20e3),
#                 (9.1e3, 20e3),
#                 (3.1e3, 20e3),
#                 (10.1e3, 20e3),
#                 (5.1e3, 20e3),
#                 (-5.1e3, 20e3),
#                 (8e3, 20e3),
#                 (10e3, 20e3)]
#
# # Combine definitions into a Cell object
# cells = dict()
# cells['Cell 1'] = st.Cell('Cell 1', cell_1_times, cell_1_xlims, cell_1_ylims)
# cells['Cell 2'] = st.Cell('Cell 2', cell_2_times, cell_2_xlims, cell_2_ylims)
# cells['Cell 3'] = st.Cell('Cell 3', cell_3_times, cell_3_xlims, cell_3_ylims)
# cells['Cell 1-2'] = st.Cell('Cell 1-2', cell_12_times, cell_12_xlims, cell_12_ylims)
#
# cells = dict()
# cells['All'] = st.Cell('All', cell_times, cell_xlims, cell_ylims)
#
# # Create the Analsysis object
# analyzer = st.Analysis(storm_lma, storm_ods, cells)
#
# # If the flashes have not been sorted into each cell, do so.
# if sort_flashes:
#     analyzer.sort_into_cells(sorted_file_name, 15)
#
# # Get the StormLMA and StormODS objects from sorted data.
# for cell in cells:
#     cells[cell].set_ods(analyzer.ods.get_cell_ods(cell))
#     cells[cell].set_lma(analyzer.lma.get_lma_from_ods(cells[cell].ods))
#     cells[cell].lma.storm.sort_index(inplace=True)
#