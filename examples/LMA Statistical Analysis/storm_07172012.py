#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/Storm-07-17-2012'
file_lma_1 = path + '/LMA/ChargeAnalysis-1of2-exported.csv'
file_lma_2 = path + '/LMA/ChargeAnalysis-2of2-exported.csv'

dates = ['07/17/2012']

storm_lma = st.StormLMA.from_lma_files([file_lma_1, file_lma_2], dates, 7, 5)

# File names and analysis flags for .ods files
sort_flashes = False
get_flash_numbers = False

sorted_file_name = path + '/Statistical Analysis/07172012-Sorted_into_cells'
sorted_pickle = sorted_file_name + '.p'
sorted_csv = sorted_file_name + '.csv'
flash_numbers_pickle = path + \
                       '/Statistical Analysis/07172012_ods_flash-numbers.p'
flash_numbers_csv = path + \
                    '/Statistical Analysis/07172012_ods_flash-numbers.csv'
original_csv = path + '/Cell 1 LMA Analysis 07172012.ods'

file_name = sorted_csv
pickle_file = sorted_pickle

# Load the most analyzed file first if it exists. If no analyzed file exists
# set the flags to do the analysis and save the analyzed data for future runs.

if not(os.path.isfile(pickle_file)):
    if not (os.path.isfile(file_name)):
        sort_flashes = True
        pickle_file = flash_numbers_pickle
        file_name = flash_numbers_csv

        if not(os.path.isfile(pickle_file)):
            if not(os.path.isfile(file_name)):
                get_flash_numbers = True
                storm_ods = st.StormODS.from_ods_file(original_csv)

            else:
                storm_ods = st.StormODS.from_ods_file(file_name)

        else:
            storm_ods = st.StormODS()
            storm_ods.from_pickle(pickle_file)
    else:
        storm_ods = st.StormODS.from_ods_file(file_name)

else:
    storm_ods = st.StormODS()
    storm_ods.from_pickle(pickle_file)

if get_flash_numbers:
    s = storm_ods.get_analyzed_flash_numbers(storm_lma, verbose=True)
    s.save_to_pickle(flash_numbers_pickle)
    s.to_csv(flash_numbers_csv)
    storm_ods = s

# Cell definitions
# Entire storm
cell_times = [datetime.datetime(2012, 7, 17, 18, 17, 0),
              datetime.datetime(2012, 7, 17, 18, 22, 0),
              datetime.datetime(2012, 7, 17, 18, 27, 0),
              datetime.datetime(2012, 7, 17, 18, 31, 0),
              datetime.datetime(2012, 7, 17, 18, 36, 0),
              datetime.datetime(2012, 7, 17, 18, 41, 0),
              datetime.datetime(2012, 7, 17, 18, 45, 0),
              datetime.datetime(2012, 7, 17, 18, 50, 0),
              datetime.datetime(2012, 7, 17, 18, 55, 0),
              datetime.datetime(2012, 7, 17, 19, 0, 0),
              datetime.datetime(2012, 7, 17, 19, 4, 0),
              datetime.datetime(2012, 7, 17, 19, 9, 0),
              datetime.datetime(2012, 7, 17, 19, 14, 0),
              datetime.datetime(2012, 7, 17, 19, 18, 0),
              datetime.datetime(2012, 7, 17, 19, 23, 0),
              datetime.datetime(2012, 7, 17, 19, 28, 0),
              datetime.datetime(2012, 7, 17, 19, 32, 0),
              datetime.datetime(2012, 7, 17, 19, 37, 0),
              datetime.datetime(2012, 7, 17, 19, 42, 0),
              datetime.datetime(2012, 7, 17, 19, 47, 0),
              datetime.datetime(2012, 7, 17, 19, 51, 0),
              datetime.datetime(2012, 7, 17, 19, 56, 0),
              datetime.datetime(2012, 7, 17, 20, 1, 0),
              datetime.datetime(2012, 7, 17, 20, 5, 0),
              datetime.datetime(2012, 7, 17, 20, 10, 0),
              datetime.datetime(2012, 7, 17, 20, 15, 0),
              datetime.datetime(2012, 7, 17, 20, 20, 0),
              datetime.datetime(2012, 7, 17, 20, 24, 0),
              datetime.datetime(2012, 7, 17, 20, 29, 0),
              datetime.datetime(2012, 7, 17, 20, 34, 0),
              datetime.datetime(2012, 7, 17, 20, 39, 0),
              datetime.datetime(2012, 7, 17, 20, 44, 0),
              datetime.datetime(2012, 7, 17, 20, 48, 0),
              datetime.datetime(2012, 7, 17, 20, 53, 0),
              datetime.datetime(2012, 7, 17, 20, 58, 0),
              datetime.datetime(2012, 7, 17, 21, 2, 0),
              datetime.datetime(2012, 7, 17, 21, 7, 0),
              datetime.datetime(2012, 7, 17, 21, 11, 0),
              datetime.datetime(2012, 7, 17, 21, 16, 0),
              datetime.datetime(2012, 7, 17, 21, 21, 0),
              datetime.datetime(2012, 7, 17, 21, 26, 0),
              datetime.datetime(2012, 7, 17, 21, 30, 0),
              datetime.datetime(2012, 7, 17, 21, 35, 0),
              datetime.datetime(2012, 7, 17, 21, 40, 0),
              datetime.datetime(2012, 7, 17, 21, 44, 0),
              datetime.datetime(2012, 7, 17, 21, 49, 0),
              datetime.datetime(2012, 7, 17, 21, 54, 0),
              datetime.datetime(2012, 7, 17, 21, 59, 0)]

cell_xlims = [(-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3)]

cell_ylims = [(-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3),
              (-50e3, 50e3)]

# Define Cell 1
cell_1_times = []

cell_1_xlims = []

cell_1_ylims = []

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

