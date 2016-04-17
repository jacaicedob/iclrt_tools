#!/usr/bin/env python

import iclrt_tools.lma.analysis.storm_analysis as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import datetime
import os

storm_ods = None
storm_lma = None
path = None


def init():
    global storm_lma, storm_ods, path

    # File names for first and second part of storm analysis
    path = '/home/jaime/Documents/ResearchTopics/Publications/' \
           'LightningEvolution/Storm-08-27-2015'
    file1 = path + '/LMA/ChargeAnalysis-1of2-exported.csv'
    file2 = path + '/LMA/ChargeAnalysis-2of2-exported.csv'

    dates = ['08/27/2015', '08/28/2015']

    file_name = path + '/Statistical Analysis/08272015-Sorted_into_cells.csv'

    if not(os.path.isfile(file_name)):
        file_name = path + '/LMA Analysis 08272015.csv'

    pickle_file = path + '/Statistical Analysis/08272015-Sorted_into_cells.p'

    if not(os.path.isfile(pickle_file)):
        pickle_file = path + \
                      '/Statistical Analysis/08272015_ods_flash-numbers.p'

    if os.path.isfile(pickle_file):
        storm_ods = st.StormODS()
        storm_ods.from_pickle(pickle_file)
    else:
        storm_ods = st.StormODS.from_ods_file(file_name)

    storm_lma = st.StormLMA.from_lma_files([file1, file2], dates)


def nice_plots():
    sns.set_context('talk', font_scale=2.0)


def sort_into_cells():
    global storm_lma, storm_ods

    # Define Cell 1
    cell_1_times = [datetime.datetime(2015, 8, 27, 22, 36, 0),
                    datetime.datetime(2015, 8, 27, 22, 40, 0),
                    datetime.datetime(2015, 8, 27, 22, 44, 0),
                    datetime.datetime(2015, 8, 27, 22, 48, 0),
                    datetime.datetime(2015, 8, 27, 22, 52, 0),
                    datetime.datetime(2015, 8, 27, 22, 56, 0),
                    datetime.datetime(2015, 8, 27, 23, 0, 0),
                    datetime.datetime(2015, 8, 27, 23, 4, 0),
                    datetime.datetime(2015, 8, 27, 23, 8, 0),
                    datetime.datetime(2015, 8, 27, 23, 13, 0),
                    datetime.datetime(2015, 8, 27, 23, 17, 0),
                    datetime.datetime(2015, 8, 27, 23, 21, 0),
                    datetime.datetime(2015, 8, 27, 23, 26, 0),
                    datetime.datetime(2015, 8, 27, 23, 30, 0),
                    datetime.datetime(2015, 8, 27, 23, 34, 0),
                    datetime.datetime(2015, 8, 27, 23, 38, 0),
                    datetime.datetime(2015, 8, 27, 23, 43, 0),
                    datetime.datetime(2015, 8, 27, 23, 47, 0),
                    datetime.datetime(2015, 8, 27, 23, 51, 0),
                    datetime.datetime(2015, 8, 27, 23, 51, 0)]


    cell_1_xlims = [(-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, -10.1e3)]

    cell_1_ylims = [(-5e3, 5e3),
                    (-5e3, 8e3),
                    (-5e3, 8e3),
                    (-5e3, 8e3),
                    (-5e3, 8e3),
                    (-5e3, 8e3),
                    (-5e3, 10e3),
                    (-5e3, 10e3),
                    (-10e3, 15e3),
                    (-11e3, 18e3),
                    (-13e3, 18e3),
                    (-13e3, 18e3),
                    (-11e3, 20e3),
                    (-11e3, 20e3),
                    (-9.9e3, 20e3),
                    (-9.9e3, 5e3),
                    (-9.9e3, 5e3),
                    (-7.9e3, 7e3),
                    (-8.9e3, 8e3),
                    (-20e3, -8.9e3)]

    cell_1_names = ['Cell 1']

    # Define Cell 1-2 (merger between cells 1 and 2)
    cell_12_times = [datetime.datetime(2015, 8, 27, 23, 56, 0),
                     datetime.datetime(2015, 8, 28, 0, 0, 0),
                     datetime.datetime(2015, 8, 28, 0, 0, 0),
                     datetime.datetime(2015, 8, 28, 0, 5, 0),
                     datetime.datetime(2015, 8, 28, 0, 5, 0),
                     datetime.datetime(2015, 8, 28, 0, 5, 0),
                     datetime.datetime(2015, 8, 28, 0, 9, 0),
                     datetime.datetime(2015, 8, 28, 0, 9, 0),
                     datetime.datetime(2015, 8, 28, 0, 9, 0),
                     datetime.datetime(2015, 8, 28, 0, 14, 0),
                     datetime.datetime(2015, 8, 28, 0, 14, 0),
                     datetime.datetime(2015, 8, 28, 0, 14, 0),
                     datetime.datetime(2015, 8, 28, 0, 19, 0),
                     datetime.datetime(2015, 8, 28, 0, 19, 0),
                     datetime.datetime(2015, 8, 28, 0, 23, 0),
                     datetime.datetime(2015, 8, 28, 0, 23, 0),
                     datetime.datetime(2015, 8, 28, 0, 28, 0)]

    cell_12_xlims = [(-20e3, 20e3),
                     (-20e3, 20e3),
                     (-6e3, 20e3),
                     (-20e3, 20e3),
                     (-12e3, 20e3),
                     (-5e3, 20e3),
                     (-20e3, 20e3),
                     (-10e3, 203),
                     (-7e3, 20e3),
                     (-20e3, 20e3),
                     (-10e3, 20e3),
                     (-5e3, 20e3),
                     (-20e3, 20e3),
                     (-7e3, 20e3),
                     (-20e3, 20e3),
                     (-5e3, 20e3),
                     (-20e3, 20e3)]

    cell_12_ylims = [(-17e3, 7.9e3),
                     (-15e3, 7.9e3),
                     (7.9e3, 20e3),
                     (-13e3, 2e3),
                     (2.1e3, 7e3),
                     (7.1e3, 20e3),
                     (-14e3, 3e3),
                     (3.1e3, 9e3),
                     (9.1e3, 20e3),
                     (-14e3, 3e3),
                     (3.1e3, 10e3),
                     (10.1e3, 20e3),
                     (-15e3, 5e3),
                     (5.1e3, 20e3),
                     (-15e3, 5e3),
                     (5.1e3, 20e3),
                     (-15e3, 5e3)]

    cell_12_names = ['Cell 1-2']

    # Define Cell 2

    cell_2_times = [datetime.datetime(2015, 8, 27, 23, 17, 0),
                    datetime.datetime(2015, 8, 27, 23, 21, 0),
                    datetime.datetime(2015, 8, 27, 23, 26, 0),
                    datetime.datetime(2015, 8, 27, 23, 30, 0),
                    datetime.datetime(2015, 8, 27, 23, 34, 0),
                    datetime.datetime(2015, 8, 27, 23, 38, 0),
                    datetime.datetime(2015, 8, 27, 23, 43, 0),
                    datetime.datetime(2015, 8, 27, 23, 47, 0),
                    datetime.datetime(2015, 8, 27, 23, 51, 0)]

    cell_2_xlims = [(-5e3, 20e3),
                    (-5e3, 20e3),
                    (-5e3, 20e3),
                    (-10e3, 20e3),
                    (-10e3, 20e3),
                    (-10e3, 10e3),
                    (-20e3, 10e3),
                    (-20e3, 10e3),
                    (-10e3, 10e3)]

    cell_2_ylims = [(-20e3, -15e3),
                    (-20e3, -13e3),
                    (-20e3, -13e3),
                    (-20e3, -13e3),
                    (-20e3, -10e3),
                    (-20e3, -10e3),
                    (-20e3, -10e3),
                    (-20e3, -8e3),
                    (-18e3, -9e3)]

    cell_2_names = ['Cell 2']

    # Define Cell 3

    cell_3_times = [datetime.datetime(2015, 8, 27, 23, 38, 0),
                    datetime.datetime(2015, 8, 27, 23, 43, 0),
                    datetime.datetime(2015, 8, 27, 23, 47, 0),
                    datetime.datetime(2015, 8, 27, 23, 51, 0),
                    datetime.datetime(2015, 8, 27, 23, 56, 0),
                    datetime.datetime(2015, 8, 28, 0, 0, 0),
                    datetime.datetime(2015, 8, 28, 0, 5, 0),
                    datetime.datetime(2015, 8, 28, 0, 5, 0),
                    datetime.datetime(2015, 8, 28, 0, 9, 0),
                    datetime.datetime(2015, 8, 28, 0, 9, 0),
                    datetime.datetime(2015, 8, 28, 0, 14, 0),
                    datetime.datetime(2015, 8, 28, 0, 14, 0),
                    datetime.datetime(2015, 8, 28, 0, 19, 0),
                    datetime.datetime(2015, 8, 28, 0, 23, 0),
                    datetime.datetime(2015, 8, 28, 0, 28, 0),
                    datetime.datetime(2015, 8, 28, 0, 33, 0)]

    cell_3_xlims = [(-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, 20e3),
                    (-20e3, -7e3),
                    (-20e3, -12.1e3),
                    (-12.1e3, -5.1e3),
                    (-20e3, -10.1e3),
                    (-10.1e3, -7.1),
                    (-20e3, -10.1e3),
                    (-10e3, -5.1e3),
                    (-20e3, -7.1e3),
                    (-20e3, -5.1e3),
                    (-20e3, -5e3),
                    (-20e3, -5e3)]

    cell_3_ylims = [(5.1e3, 20e3),
                    (5.1e3, 20e3),
                    (7.1e3, 20e3),
                    (8.1e3, 20e3),
                    (8e3, 20e3),
                    (8.0e3, 20e3),
                    (2.1e3, 20e3),
                    (7.1e3, 20e3),
                    (3.1e3, 20e3),
                    (9.1e3, 20e3),
                    (3.1e3, 20e3),
                    (10.1e3, 20e3),
                    (5.1e3, 20e3),
                    (-5.1e3, 20e3),
                    (8e3, 20e3),
                    (10e3, 20e3)]

    cell_3_names = ['Cell 3']

    # Split the flashes into each cell

    results_1 = storm_ods.sort_flashes_into_cells(storm_lma,
                                                  cell_1_times,
                                                  cell_1_xlims,
                                                  cell_1_ylims,
                                                  cell_1_names,
                                                  inplace=False)

    results_12 = storm_ods.sort_flashes_into_cells(storm_lma,
                                                  cell_12_times,
                                                  cell_12_xlims,
                                                  cell_12_ylims,
                                                  cell_12_names,
                                                  inplace=False)

    results_2 = storm_ods.sort_flashes_into_cells(storm_lma,
                                                  cell_2_times,
                                                  cell_2_xlims,
                                                  cell_2_ylims,
                                                  cell_2_names,
                                                  inplace=False)

    results_3 = storm_ods.sort_flashes_into_cells(storm_lma,
                                                  cell_3_times,
                                                  cell_3_xlims,
                                                  cell_3_ylims,
                                                  cell_3_names,
                                                  inplace=False)

    # Merge all the Cell classifications into the storm_ods DataFrame

    # Get the Series for each cell
    df1 = pd.DataFrame(results_1['Cell'])
    df12 = pd.DataFrame(results_12['Cell'])
    df2 = pd.DataFrame(results_2['Cell'])
    df3 = pd.DataFrame(results_3['Cell'])

    # Reset their indices to aid in the merge function
    df1.reset_index(inplace=True)
    df12.reset_index(inplace=True)
    df2.reset_index(inplace=True)
    df3.reset_index(inplace=True)

    # Merge Cell 1 and 2 together.
    temp = pd.merge(df1, df2, how='outer')

    # Merge Cell 1,2 and 3 together.
    temp = pd.merge(temp, df3, how='outer')

    # Merge Cell 1,2,3 and 12 together.
    temp = pd.merge(temp, df12, how='outer')

    # Sort the entries by the cell names
    temp.sort_values(by='Cell', inplace=True)

    # Remove the duplicate times, set the index, and sort the data
    temp.drop_duplicates(subset='DateTime', inplace=True)
    temp.set_index('DateTime', inplace=True)
    temp.sort_index(inplace=True)

    storm_ods.storm.loc[:, 'Cell'] = temp
    file_csv = path + '/Statistical Analysis/08272015-Sorted_into_cells.csv'
    storm_ods.storm.to_csv(file_csv)

    file_p = path + '/Statistical Analysis/08272015-Sorted_into_cells.p'
    storm_ods.save_to_pickle(file_p)


def get_cell_ods(cell_name):
    global storm_ods

    temp = storm_ods.storm.copy()
    temp = temp.groupby('Cell').get_group(cell_name)

    return st.StormODS(temp)


def get_lma_from_ods(storm_ods):
    global storm_lma

    temp = storm_ods.storm.dropna(subset=['Cell'])
    temp = temp['flash-number'].dropna().unique()

    numbers = []
    for n in temp:
        if type(n) == tuple:
            for m in n:
                numbers.append(m)
        else:
            numbers.append(n)

    print(len(temp))
    print(len(numbers))

    flashes = []
    for n in numbers:
        flashes.append(
            storm_lma.storm[storm_lma.storm['flash-number'] == n])

    lma = pd.concat(flashes)
    return st.StormLMA(lma)


def get_cell_initial_plotter(cell_name):
    global storm_ods, storm_lma

    cell_ods = get_cell_ods(cell_name)
    cell_lma = get_lma_from_ods(cell_ods)

    numbers = cell_lma.storm['flash-number'].unique()

    return cell_lma.get_initial_plotter_from_number(numbers)


def get_cell_plotter(cell_name):
    global storm_ods, storm_lma

    cell_ods = get_cell_ods(cell_name)
    cell_lma = get_lma_from_ods(cell_ods)

    numbers = cell_lma.storm['flash-number'].unique()

    return cell_lma.get_flash_plotter_from_number(numbers)


def plot_flash_areas(cell_name):
    cell = get_cell_ods(cell_name)

    for t in cell.storm['Type'].unique():
        cell.analyze_flash_areas(flash_type=t)


def plot_initiation_heights(cell_name):
    cell = get_cell_ods(cell_name)

    for t in cell.storm['Type'].unique():
        cell.analyze_initiation_heights(flash_type=t)


def plot_ics_vs_cgs_areas(cell_name):
    cell = get_cell_ods(cell_name)

    ics = cell.get_flash_type('IC')
    cgs = cell.get_flash_type('-CG')

    ic_series = ics['Area (km^2)']
    cg_series = cgs['Area (km^2)']

    data_frame = pd.DataFrame({' ICs': ic_series, 'CGs': cg_series})
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    data_frame.plot.hist(alpha=0.5, ax=ax)

    title = 'Histogram of flash areas for ICs ' \
            'and -CGs\n{0}'.format(cell_name)
    ax.set_title(title)
    ax.set_xlabel(r'Flash Area (km$^2$)')
    ax.legend()


def plot_ics_vs_cgs_init_height(cell_name):
    cell = get_cell_ods(cell_name)

    ics = cell.get_flash_type('IC')
    cgs = cell.get_flash_type('-CG')

    ic_series = ics['Initiation Height (km)']
    cg_series = cgs['Initiation Height (km)']

    data_frame = pd.DataFrame({' ICs': ic_series, 'CGs': cg_series})
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    data_frame.plot.hist(alpha=0.5, ax=ax)
    title = 'Histogram of initiation heights for ICs ' \
            'and -CGs\n{0}'.format(cell_name)
    ax.set_title(title)
    ax.set_xlabel('Initiation Height (km)')
    ax.legend()


def main():
    init()
    sort_into_cells()

    # cell_1_ods = get_cell_ods('Cell 1')
    # cell_1_lma = get_lma_from_ods(cell_1_ods)
    #
    # cell_1_lma.plot_all_charge_regions()
    # p1 = get_cell_initial_plotter('Cell 1')

    # plot_flash_areas('Cell 1')
    # plot_initiation_heights('Cell 1')

    # plot_ics_vs_cgs_areas('Cell 1')
    # plot_ics_vs_cgs_init_height('Cell 1')

    # p = get_cell_initial_plotter('Cell 1')
    # p.plot_plan()
    # plt.show()

    # cell_2_ods = get_cell_ods('Cell 2')
    # len(cell_2_ods.storm.index)

    # cell_3_ods = get_cell_ods('Cell 3')
    # cell_3_lma = get_lma_from_ods(cell_3_ods)
    #
    # p3 = get_cell_initial_plotter('Cell 3')

    # cell_3_lma.plot_all_charge_regions(show_plot=True)
    # print(len(cell_3_ods.storm.index))

    # nice_plots()
    # fig, ax = plt.subplots(1, 1, figsize=(12,6))
    # p1.plot_plan(fig=fig, ax=ax, c='blue')
    # p3.plot_plan(fig=fig, ax=ax, c='green')
    # plt.show()

if __name__ == '__main__':
    main()


