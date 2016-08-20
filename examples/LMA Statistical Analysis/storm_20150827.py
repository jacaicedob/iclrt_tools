#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os
import sys

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2015-08-27'

# All Flashes
ods_all = path + '/ods/LMA Analysis 08272015.csv'
lma_all = path + '/Pandas/Storm_20150827_pandas_all_lma.csv'
csv_all_source_count = path + \
                       '/Pandas/Storm_20150827_pandas_all_lma_source_count' \
                       '.csv'

# Big Flashes
lma_big = path + '/Pandas/Storm_20150827_pandas_big_lma.csv'
csv_big_source_count = path + \
                       '/Pandas/Storm_20150827_pandas_big_lma_source_count' \
                       '.csv'

lma_big_pre_final = path + '/Pandas/Storm_20150827_pandas_big_pre_final_lma.csv'
csv_big_pre_final_source_count = path + '/Pandas/Storm_20150827_pandas_big_' \
                                 'pre_final_lma_source_count.csv'

lma_big_final = path + '/Pandas/Storm_20150827_pandas_big_final_lma.csv'
csv_big_final_source_count = path + '/Pandas/Storm_20150827_pandas_big_final' \
                                    '_lma_source_count.csv'

# Needed to split duplicates
temp_duplicates = path + '/Pandas/temp_dups.csv'

# Dates
dates = ['08/27/2015', '08/28/2015']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(lma_all)):
    # Read in the individual files and save them out to a CSV file
    xlma_files = [path + '/xlma/ChargeAnalysis-1of2.exported.csv',
                  path + '/xlma/ChargeAnalysis-2of2.exported.csv']

    print("Reading all xlma files...")
    storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
    print("Converting coordinates to meters...")
    storm_lma.convert_latlon_to_m(verbose=True)
    print("Saving xlma all to CSV...")
    storm_lma.save_to_csv(lma_all)
    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(lma_big)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        # Read in the information
        storm_lma = st.StormLMA.from_lma_files([lma_all], [dates[0]])

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', lma_big)
    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)

if not(os.path.isfile(csv_all_source_count)):
    print("Loading all flashes from CSV...")
    storm_lma = st.StormLMA.from_lma_files([lma_all], [dates[0]])
    print("Saving all flash number counts to CSV...")
    storm_lma.save_flash_number_count(csv_all_source_count)

if not(os.path.isfile(csv_big_source_count)):
    print("Loading the big flashes from CSV...")
    storm_lma_big = st.StormLMA.from_lma_files([lma_big], [dates[0]])
    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)

# def split_flashes():
#     try:
#         storm_lma = st.StormLMA.from_lma_files([lma_big_lessdups,
#                                                 lma_big_lessdups_2],
#                                                dates)
#
#     except OSError:
#         storm_lma = st.StormLMA.from_lma_files([lma_big,
#                                                 lma_big_2],
#                                                dates)
#
#     try:
#         duplicates = st.pd.read_csv(temp_duplicates,
#                                     names=['index', 'flash-number'])
#     except OSError:
#         duplicates = st.pd.read_csv(csv_big_matched_duplicates,
#                                     names=['index', 'flash-number'])
#
#     storm_lma.filter_x(lims=[-35e3, 35e3], inplace=True)
#     storm_lma.filter_y(lims=[-35e3, 35e3], inplace=True)
#     storm = storm_lma.copy()
#     dups = duplicates['flash-number'].unique()
#
#     for num in range(len(dups)):
#         print("Flash {0}: {1} out of {2}".format(dups[num],
#                                                  num + 1, len(dups)))
#
#         p = storm.get_flash_plotter_from_number(dups[num])
#         p.set_coloring('charge')
#
#         p.plot_plan()
#         p.ax_plan.set_title("Flash {0} out of {1}".format(num + 1,
#                                                           len(dups)))
#         st.df.plt.show()
#
#         default = "n"
#         response = input("Split into flashes? [y/N]")
#
#         if response.lower() != "y":
#             response = default
#
#         if response == "y":
#             print("  Flash number: ", dups[num])
#             print("  x lims: ", p.ax_plan.get_xlim())
#             print("  y lims: ", p.ax_plan.get_ylim())
#
#             # Get plot limits
#             xlims = p.ax_plan.get_xlim()
#             ylims = p.ax_plan.get_ylim()
#
#             # Get the maximum flash number of storm
#             new_number = storm.storm['flash-number'].max() + 10
#
#             # Get the sources for the current flash number
#             data = storm.storm[storm.storm['flash-number'] == dups[num]]
#
#             # Sort out the new flashes using the plot limits. results holds
#             # the DateTimeIndex for the sources inside the plot limits, and
#             # rest hold all other sources in the data DataFrame
#             results = []
#             rest = []
#
#             for index, row in data.iterrows():
#                 if xlims[0] < row['x(m)'] < xlims[1]:
#                     if ylims[0] < row['y(m)'] < ylims[1]:
#                         results.append(index)
#                     else:
#                         rest.append(index)
#                 else:
#                     rest.append(index)
#
#             # Set new flash numbers for both sets of sources
#             data.set_value(results, 'flash-number', new_number)
#             data.set_value(rest, 'flash-number', new_number + 10)
#
#             # Combine with the master DataFrame and remove the entries
#             # with the old flash number from the master DataFrame
#             final = st.pd.concat([storm.storm, data])
#             storm.storm = final[final['flash-number'] != dups[num]]
#
#             # Save out results to allow for resume
#             s = st.pd.Series(dups[num + 1:], name="Duplicates")
#             s.to_csv(temp_duplicates)
#             storm.save_to_csv(lma_big_lessdups)
#
#         else:
#             # Save out results to allow for resume
#             s = st.pd.Series(dups[num + 1:], name="Duplicates")
#             s.to_csv(temp_duplicates)


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

        p = storm_big.get_flash_plotter_from_number(nums[i])
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
# sys.exit(1)
print("- Loading data for all big flashes...")
# storm_big = st.StormLMA.from_lma_files([lma_big], [dates[0]])
storm_big = st.StormLMA.from_lma_files([lma_big_final], [dates[0]])

# Get all unique flash numbers
print("- Getting all unique flash numbers")
nums = storm_big.storm['flash-number'].unique()

# nums = st.pd.read_csv(path +
#                       '/Pandas/Figures/FirstRun/Storm_20150827_FirstRun_' \
#                       'reanalyze.csv')
# nums = nums['flash-number'].unique()

# Define save directory
save_dir = path + '/Pandas/Figures'
# save_dir = path + '/Pandas/Figures/FinalRun/All'

plot_big_flashes(storm_big, nums, save_dir)
sys.exit(1)

split_flashes()