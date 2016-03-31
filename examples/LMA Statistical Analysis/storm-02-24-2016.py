#!/usr/bin/env python

import pandas as pd
import datetime

import iclrt_tools.lma.analysis.storm_analysis as st

def init_lma():
    # File names for first and second cell of storm
    cell_1_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1120-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1130-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1140-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1150-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1200-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1210-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1220-exported.csv']


    # Create Pandas objects
    cell_1_pds = []

    for file_name in cell_1_files:
        print(file_name)
        cell_1_pds.append(pd.read_csv(file_name))

    # Combine all the DataFrames into one bigger one per cell
    cell_1 = pd.concat(cell_1_pds)

    # Insert a column with the appropriate date for each cell
    cell_1.insert(0, 'Date', '02/24/2016')
    cell_1['time'] = cell_1['time(UT-sec-of-day)'] * 1e-3

    return cell_1


def init_ods():
    file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/Cell1 Analysis 02242016.csv'

    # Read in the file
    storm = pd.read_csv(file_name)

    # Combine the date and time columns into a single datetime column
    storm.insert(0, 'DateTime',
                 ['{0} {1}'.format(storm['Date'][i], storm['Time'][i]) for i in
                  range(len(storm))])
    storm['DateTime'] = pd.to_datetime(storm['DateTime'],
                                       format='%m/%d/%y %H:%M:%S.%f')

    # Convert the values in the duration column to timedelta objects
    storm['Duration(s)'] = pd.to_timedelta(storm['Duration (ms)'], unit='ms')

    # Remove unnecessary colums
    _ = storm.pop('Date')
    _ = storm.pop('Time')
    _ = storm.pop('Flash')
    _ = storm.pop('Comments')
    _ = storm.pop('Duration (ms)')

    return storm


if __name__ == '__main__':
    storm_lma = st.Storm(init_lma())
    storm_ods = st.Storm(init_ods())

    storm_ods.get_flash_rate(category='IC')
    storm_lma.plot_all_charge_regions(show_plot=True)
