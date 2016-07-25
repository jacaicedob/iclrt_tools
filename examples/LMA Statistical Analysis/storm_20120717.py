#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import datetime
import os

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

# ODS-LMA Matched Big Flashes
lma_big_matched = path + '/Pandas/' \
                  'Storm_20120717_pandas_big_matched_lma.csv'
ods_big_matched = path + '/Pandas/' \
                  'Storm_20120717_pandas_big_matched_ods.csv'
ods_big_matched_2 = path + '/Pandas/' \
                    'Storm_20120717_pandas_big_matched_ods_2.csv'

csv_big_matched_duplicates = path + '/Pandas/Storm_20120717_pandas_big_' \
                            'matched_duplicates.csv'

# Needed to split duplicates
temp_duplicates = path + '/Pandas/temp_dups.csv'

# Flashes After Splitting duplicates
lma_big_lessdups = path + \
                   '/Pandas/Storm_20120717_pandas_big_lessduplicates_lma' \
                   '.csv'

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
    print("Starting split-flashes routine...")
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
            s = st.pd.Series(dups[num+1:], name="Duplicates")
            s.to_csv(temp_duplicates)
            storm.save_to_csv(lma_big_lessdups)

        else:
            # Save out results to allow for resume
            s = st.pd.Series(dups[num + 1:], name="Duplicates")
            s.to_csv(temp_duplicates)

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

    storm_ods = st.StormODS.from_ods_all(ods_all[0])
    storm_ods_2 = st.StormODS.from_ods_all(ods_all[1])

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

