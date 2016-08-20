#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os
import sys

# File names containing all data
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2012-07-17'

# All Flashes
ods_all = [path + '/ods/Cell1 Analysis 07172012.csv',
           path + '/ods/Cell2 Analysis 07172012.csv']
lma_all = path + '/Pandas/Storm_20120717_pandas_all_lma.csv'
csv_all_source_count = path + \
                       '/Pandas/Storm_20120717_pandas_all_lma_source_count' \
                       '.csv'

# Big Flashes
lma_big = path + '/Pandas/Storm_20120717_pandas_big_lma.csv'
csv_big_source_count = path + \
                       '/Pandas/Storm_20120717_pandas_big_lma_source_count' \
                       '.csv'

lma_big_final = path + '/Pandas/Storm_20120717_pandas_big_final_lma.csv'
csv_big_final_source_count = path + '/Pandas/Storm_20120717_pandas_big_final' \
                             '_lma_source_count.csv'

# Needed to split duplicates
temp_duplicates = path + '/Pandas/temp_dups.csv'

# Dates
dates = ['07/17/2012']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(lma_all)):
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
    storm_lma.save_to_csv(lma_all)

if not(os.path.isfile(lma_big)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([lma_all], dates)

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', lma_big)

    storm_lma_big = st.StormLMA.from_lma_files([lma_big],
                                               dates)

if not(os.path.isfile(csv_all_source_count)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([lma_all], dates)

    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(csv_big_source_count)):
    if storm_lma_big is None:
        print("Loading the big flashes from CSV...")
        storm_lma_big = st.StormLMA.from_lma_files([lma_big],
                                               dates)

    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)


def plot_big_flashes(storm_big, nums, save_dir):
    print("Plotting and saving big flashes:")
    print("- Removing flash numbers already plotted...")
    series = st.pd.Series(nums, name='flash-number')
    series = series.reset_index()

    files = [s[6:-4] for s in os.listdir(save_dir)]
    for f in files:
        series = series[series['flash-number'] != int(f)]

    nums = series['flash-number'].unique()

    # Start loop
    print("- Starting loop:")
    for i in range(len(nums)):
        print("  - Flash {0}: {1} of {2}".format(nums[i], i+1,
                                                 len(nums)))

        p = storm_big.get_flash_plotter_from_number(nums[i], path +
                                                    '/Pandas/Figures')
        p.filter_num_stations(6)
        p.filter_rc2(1)
        p.set_coloring('charge')

        if len(p.plot_data['t']) < 1:
            print("       * No data for Flash {0}".format(nums[i]))
            continue

        try:
            p.plot_all()
        except ValueError:
            print('       * Skipping {0}...'.format(nums[i]))
            continue

        p.ax_all_alt_t.set_title("Flash {0}".format(nums[i]))

        save_file = save_dir + '/flash_{0}.png'.format(nums[i])
        p.fig_all.savefig(save_file, dpi=300, format='png')
        st.df.plt.close()

# Read in data
print("- Loading data for all big flashes...")
# storm_big = st.StormLMA.from_lma_files([lma_big], dates)
storm_big = st.StormLMA.from_lma_files([lma_big_final], dates)

# Get all unique flash numbers
print("- Getting all unique flash numbers")
nums = storm_big.storm['flash-number'].unique()

# nums = st.pd.read_csv(path + '/Pandas/Figures/FirstRun_reanalyze.csv')
# nums = nums['flash-number'].unique()

# Define save directory
save_dir = path + '/Pandas/Figures'
# save_dir = path + '/Pandas/Figures/FirstRun/AnalyzeAgain'

plot_big_flashes(storm_big, nums, save_dir)
sys.exit(1)
split_flashes()

