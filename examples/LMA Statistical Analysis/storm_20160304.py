#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os
import sys

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-03-04'

# All Flashes
ods_all = [path + '/ods/Cell1 Analysis 03042016.csv',
           path + '/ods/Cell2 Analysis 03042016.csv']
lma_all = path + '/Pandas/Storm_20160304_pandas_all_lma.csv'
csv_all_source_count = path + '/Pandas/Storm_20160304_pandas_all_lma_' \
                       'source_count.csv'

# Big Flashes
lma_big = path + '/Pandas/Storm_20160304_pandas_big_lma.csv'
csv_big_source_count = path + '/Pandas/Storm_20160304_pandas_big_lma_' \
                       'source_count.csv'

lma_big_final = path + '/Pandas/Storm_20160304_pandas_big_final_lma.csv'
csv_big_final_source_count = path + '/Pandas/Storm_20160304_pandas_big_final' \
                             '_lma_source_count.csv'

# ODS-LMA Matched Big Flashes
lma_big_matched = path + '/Pandas/Storm_20160304_pandas_big_matched_lma.csv'
ods_big_matched = path + '/Pandas/Storm_20160304_pandas_big_matched_ods.csv'
ods_big_matched_2 = path + '/Pandas/Storm_20160304_pandas_big_matched' \
                    '_ods_2.csv'
csv_big_matched_duplicates = path + '/Pandas/Storm_20160304_pandas_big_' \
                             'matched_duplicates.csv'

# Needed to split duplicates
temp_duplicates = path + '/Pandas/temp_dups.csv'

# Flashes After Splitting duplicates
lma_big_lessdups = path + '/Pandas/Storm_20160304_pandas_big_lessduplicates_' \
                   'lma.csv'

# ODS-LMA Matched Flashes After Splitting duplicates
lma_big_lessdups_matched = path + '/Pandas/Storm_20160304_pandas_big_' \
                           'lessduplicates_matched_lma.csv'
ods_big_lessdups_matched = path + '/Pandas/Storm_20160304_pandas_big_' \
                           'lessduplicates_matched_ods.csv'
ods_big_lessdups_matched_2 = path + '/Pandas/Storm_20160304_pandas_big_' \
                             'lessduplicates_matched_ods_2.csv'
csv_big_lessdups_matched_duplicates = path + '/Pandas/Storm_20160304_pandas_' \
                                      'big_lessduplicates_matched_duplicates' \
                                      '.csv'

# Dates
dates = ['03/04/2016']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

# if not(os.path.isfile(lma_all)):
#     # Read in the individual files and save them out to a CSV file
#     xlma_files = [path + '/xlma/ChargeAnalysis_20160304_0540.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0550.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0600.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0610.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0620.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0630.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0640.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0650.exported.csv',
#                   path + '/xlma/ChargeAnalysis_20160304_0700.exported.csv']
#
#     print("Reading all xlma files...")
#     storm_lma = st.StormLMA.from_lma_files(xlma_files, dates)
#     print("Converting coordinates to meters...")
#     storm_lma.convert_latlon_to_m(verbose=True)
#     print("Saving xlma all to CSV...")
#     storm_lma.save_to_csv(lma_all)
#
# if not (os.path.isfile(lma_big)):
#     if storm_lma is None:
#         print("Loading all flashes from CSV...")
#         storm_lma = st.StormLMA.from_lma_files([lma_all], dates)
#
#     print("Saving big flashes to CSV...")
#     storm_lma.save_flashes_by_size('big', lma_big)
#
# if not (os.path.isfile(csv_all_source_count)):
#     if storm_lma is None:
#         print("Loading all flashes from CSV...")
#         storm_lma = st.StormLMA.from_lma_files([lma_all], dates)
#
#     print("Saving all flash number counts to CSV...")
#     storm_lma.save_flash_number_count(csv_all_source_count)
#
# if not (os.path.isfile(csv_big_source_count)):
#     if storm_lma_big is None:
#         print("Loading the big flashes from CSV...")
#         storm_lma_big = st.StormLMA.from_lma_files([lma_big],
#                                                    dates)
#
#     print("Saving big flash number counts to CSV...")
#     storm_lma_big.save_flash_number_count(csv_big_source_count)

# if not (os.path.isfile(lma_big_matched)) or \
#    not (os.path.isfile(ods_big_matched)) or \
#    not (os.path.isfile(ods_big_matched_2)) or \
#    not (os.path.isfile(csv_big_matched_duplicates)):
#
#     print("Loading the big flashes from CSV...")
#     # Read in the information
#     storm_lma = st.StormLMA.from_lma_files([lma_big], dates)
#     storm_lma.filter_x(lims=[-50e3, 50e3], inplace=True)
#     storm_lma.filter_y(lims=[-50e3, 50e3], inplace=True)
#
#     storm_ods = st.StormODS.from_csv_file(ods_all[0])
#     storm_ods_2 = st.StormODS.from_csv_file(ods_all[1])
#
#     print("Matching the LMA flashes to the ODS entries...")
#     # Match the LMA flash numbers with the ODS entries
#     result, dups = storm_ods.get_analyzed_flash_numbers(storm_lma,
#                                                         verbose=True,
#                                                         return_duplicates=True)
#     result_2, dups_2 = storm_ods_2.get_analyzed_flash_numbers(storm_lma,
#                                                               verbose=True,
#                                                               return_duplicates=True)
#
#     # Get the matched DataFrames
#     print("Getting the matches...")
#     ods_matched = result[~st.pd.isnull(result['flash-number'])]
#     numbers = ods_matched['flash-number'].unique()
#
#     ods_matched_2 = result_2[~st.pd.isnull(result_2['flash-number'])]
#     numbers_2 = ods_matched_2['flash-number'].unique()
#
#     numbers = list(numbers) + list(numbers_2)
#     print("Number of matched flash numbers:", len(numbers))
#     lma_matched = storm_lma.get_sources_from_flash_number(numbers)
#
#     dups = st.pd.concat([dups, dups_2], ignore_index=True)
#     dups = dups.reset_index()
#     dups.drop_duplicates('duplicates', inplace=True)
#     dups = dups['duplicates']
#     print("Total duplicate/multiple flashes: ", len(dups))
#
#     # Save to CSV
#     print("Saving matches to CSV...")
#     print("  Saving LMA...")
#     lma_matched.to_csv(lma_big_matched, index=False)
#     print("  Saving ODS...")
#     ods_matched.to_csv(ods_big_matched, index=False)
#     ods_matched_2.to_csv(ods_big_matched_2, index=False)
#     print("Saving the duplicate flash number list...")
#     dups.to_csv(csv_big_matched_duplicates)


def split_flashes():
    try:
        storm_lma = st.StormLMA.from_lma_files([lma_big_lessdups], dates)

    except OSError:
        storm_lma = st.StormLMA.from_lma_files([lma_big], dates)

    try:
        duplicates = st.pd.read_csv(temp_duplicates,
                                    names=['index', 'flash-number'])
    except OSError:
        duplicates = st.pd.read_csv(csv_big_matched_duplicates,
                                    names=['index', 'flash-number'])

    storm_lma.filter_x(lims=[-50e3, 50e3], inplace=True)
    storm_lma.filter_y(lims=[-50e3, 50e3], inplace=True)
    storm = storm_lma.copy()
    dups = duplicates['flash-number'].unique()

    for num in range(len(dups)):
        print("Flash {0}: {1} out of {2}".format(dups[num],
                                                 num + 1, len(dups)))

        p = storm.get_flash_plotter_from_number(dups[num])
        p.set_coloring('charge')

        p.plot_plan()
        p.ax_plan.set_title("Flash {0} out of {1}".format(num + 1,
                                                          len(dups)))
        st.df.plt.show()

        default = "n"
        response = input("Split into flashes? [y/N]")

        if response.lower() != "y":
            response = default

        if response == "y":
            print("  Flash number: ", dups[num])
            print("  x lims: ", p.ax_plan.get_xlim())
            print("  y lims: ", p.ax_plan.get_ylim())

            # Get plot limits
            xlims = p.ax_plan.get_xlim()
            ylims = p.ax_plan.get_ylim()

            # Get the maximum flash number of storm
            new_number = storm.storm['flash-number'].max() + 10

            # Get the sources for the current flash number
            data = storm.storm[storm.storm['flash-number'] == dups[num]]

            # Sort out the new flashes using the plot limits. results holds
            # the DateTimeIndex for the sources inside the plot limits, and
            # rest hold all other sources in the data DataFrame
            results = []
            rest = []

            for index, row in data.iterrows():
                if xlims[0] < row['x(m)'] < xlims[1]:
                    if ylims[0] < row['y(m)'] < ylims[1]:
                        results.append(index)
                    else:
                        rest.append(index)
                else:
                    rest.append(index)

            # Set new flash numbers for both sets of sources
            data.set_value(results, 'flash-number', new_number)
            data.set_value(rest, 'flash-number', new_number + 10)

            # Combine with the master DataFrame and remove the entries
            # with the old flash number from the master DataFrame
            final = st.pd.concat([storm.storm, data])
            storm.storm = final[final['flash-number'] != dups[num]]

            # Save out results to allow for resume
            s = st.pd.Series(dups[num + 1:], name="Duplicates")
            s.to_csv(temp_duplicates)
            storm.save_to_csv(lma_big_lessdups)

        else:
            # Save out results to allow for resume
            s = st.pd.Series(dups[num + 1:], name="Duplicates")
            s.to_csv(temp_duplicates)


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

if not (os.path.isfile(lma_big_lessdups_matched)) or \
        not (os.path.isfile(ods_big_lessdups_matched)) or \
        not (os.path.isfile(ods_big_lessdups_matched_2)) or \
        not (os.path.isfile(csv_big_lessdups_matched_duplicates)):
    print("Loading the big flashes from CSV...")
    # Read in the information
    storm_lma = st.StormLMA.from_lma_files([lma_big_lessdups], dates)
    storm_lma.filter_x(lims=[-50e3, 50e3], inplace=True)
    storm_lma.filter_y(lims=[-50e3, 50e3], inplace=True)

    storm_ods = st.StormODS.from_csv_file(ods_all[0])
    storm_ods_2 = st.StormODS.from_csv_file(ods_all[1])

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
    dups = dups.reset_index()
    dups.drop_duplicates('duplicates', inplace=True)
    dups = dups['duplicates']
    print("Total duplicate/multiple flashes: ", len(dups))

    # Save to CSV
    print("Saving matches to CSV...")
    print("  Saving LMA...")
    lma_matched.to_csv(lma_big_lessdups_matched, index=False)
    print("  Saving ODS...")
    ods_matched.to_csv(ods_big_lessdups_matched, index=False)
    ods_matched_2.to_csv(ods_big_lessdups_matched_2, index=False)
    print("Saving the duplicate flash number list...")
    dups.to_csv(csv_big_lessdups_matched_duplicates)





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
# cell_1_ods_all = path + 'Cell1 Analysis 03042016.csv'
# cell_2_ods_all = path + 'Cell2 Analysis 03042016.csv'
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
#     storm_1_ods = st.StormODS.from_csv_file(cell_1_ods_all)
# else:
#     storm_1_ods = st.StormODS()
#     storm_1_ods.from_pickle(cell_1_ods_pickle)
#
# # Load Cell 2 ods
# if not(os.path.isfile(cell_2_ods_pickle)):
#     storm_2_ods = st.StormODS.from_csv_file(cell_2_ods_all)
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
