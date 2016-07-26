#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os
import sys

# File names for first and second part of LMA storm analysis
path = '/home/jaime/Documents/ResearchTopics/Publications/' \
       'LightningEvolution/StatisticalAnalysis/2016-03-25'

# All flashes
ods_all = [path + '/ods/Cell 1 Analysis 03252016.csv',
           path + '/ods/Cell 2 Analysis 03252016.csv']
lma_all = path + '/Pandas/Storm_20160325_pandas_all_lma.csv'
csv_all_source_count = path + '/Pandas/Storm_20160325_pandas_all_lma_' \
                       'source_count.csv'

# Big Flashes
lma_big = path + '/Pandas/Storm_20160325_pandas_big_lma.csv'
csv_big_source_count = path + '/Pandas/Storm_20160325_pandas_big_lma_' \
                       'source_count.csv'

# ODS-LMA Matched Big Flashes
lma_big_matched = path + '/Pandas/Storm_20160325_pandas_big_matched_lma.csv'
ods_big_matched = path + '/Pandas/Storm_20160325_pandas_big_matched_ods.csv'
ods_big_matched_2 = path + '/Pandas/Storm_20160325_pandas_big_matched_ods_2.csv'
csv_big_matched_duplicates = path + '/Pandas/Storm_20160325_pandas_big_' \
                             'matched_duplicates.csv'

# Needed to split duplicates
temp_duplicates = path + '/Pandas/temp_dups.csv'

# Flashes After Splitting duplicates
lma_big_lessdups = path + \
                   '/Pandas/Storm_20160325_pandas_big_lessduplicates_lma' \
                   '.csv'
lma_big_lessdups_2 = path + \
                     '/Pandas/Storm_20150828_pandas_big_lessduplicates' \
                     '_lma.csv'

# ODS-LMA Matched Flashes After Splitting duplicates
lma_big_lessdups_matched = path + '/Pandas/Storm_20120717_pandas_big_' \
                           'lessduplicates_matched_lma.csv'
ods_big_lessdups_matched = path + '/Pandas/Storm_20120717_pandas_big_' \
                           'lessduplicates_matched_ods.csv'
ods_big_lessdups_matched_2 = path + '/Pandas/Storm_20120717_pandas_big_' \
                             'lessduplicates_matched_ods_2.csv'
csv_big_lessdups_matched_duplicates = path + '/Pandas/Storm_20120717_pandas_big_' \
                              'lessduplicates_matched_duplicates.csv'

# Dates
dates = ['03/25/2016']

# Load or Initialize then load all the data from the files above.
storm_lma = None
storm_lma_big = None

if not(os.path.isfile(lma_all)):
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
    storm_lma.save_to_csv(lma_all)

if not (os.path.isfile(lma_big)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([lma_all], dates)

    print("Saving big flashes to CSV...")
    storm_lma.save_flashes_by_size('big', lma_big)

if not (os.path.isfile(csv_all_source_count)):
    if storm_lma is None:
        print("Loading all flashes from CSV...")
        storm_lma = st.StormLMA.from_lma_files([lma_all], dates)

    print("Saving all flash number counts to CSV...")

    storm_lma.save_flash_number_count(csv_all_source_count)

if not (os.path.isfile(csv_big_source_count)):
    if storm_lma_big is None:
        print("Loading the big flashes from CSV...")
        storm_lma_big = st.StormLMA.from_lma_files([lma_big],
                                                   dates)

    print("Saving big flash number counts to CSV...")
    storm_lma_big.save_flash_number_count(csv_big_source_count)

if not (os.path.isfile(lma_big_matched)) or \
   not (os.path.isfile(ods_big_matched)) or \
   not (os.path.isfile(ods_big_matched_2)) or \
   not (os.path.isfile(csv_big_matched_duplicates)):

    print("Loading the big flashes from CSV...")
    # Read in the information
    storm_lma = st.StormLMA.from_lma_files([lma_big], dates)
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
    lma_matched.to_csv(lma_big_matched, index=False)
    print("  Saving ODS...")
    ods_matched.to_csv(ods_big_matched, index=False)
    ods_matched_2.to_csv(ods_big_matched_2, index=False)
    print("Saving the duplicate flash number list...")
    dups.to_csv(csv_big_matched_duplicates)


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


def plot_big_flashes():
    print("Plotting and saving big flashes:")
    # Read in data
    print("- Loading data for all big flashes...")
    storm_big = st.StormLMA.from_lma_files([lma_big], dates)

    # Get all unique flash numbers
    print("- Getting all unique flash numbers")
    nums = storm_big.storm['flash-number'].unique()

    # Define save directory
    save_dir = path + '/Pandas/Figures'

    # Start loop
    print("- Starting loop:")
    for i in range(len(nums)):
        print("  - Flash {0}: {1} of {2}".format(nums[i], i+1,
                                                 len(nums)))

        p = storm_big.get_flash_plotter_from_number(nums[i])
        p.filter_num_stations(6)
        p.filter_rc2(1)
        p.set_coloring('charge')

        p.plot_all()
        p.ax_all_alt_t.set_title("Flash {0}".format(nums[i]))

        save_file = save_dir + '/flash_{0}.png'.format(nums[i])
        p.fig_all.savefig(save_file, dpi=300, format='png')
        st.df.plt.close()

plot_big_flashes()
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
