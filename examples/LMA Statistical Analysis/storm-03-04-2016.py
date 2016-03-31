#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st


def init_lma():
    # File names for first and second cell of storm
    cell_1_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0540-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0550-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0600-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0610-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0620-exported.csv']

    cell_2_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0600-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0610-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0620-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0630-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0640-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0650-exported.csv',
                    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0700-exported.csv']

    # Create Pandas objects
    cell_1_pds = []
    cell_2_pds = []

    for file_name in cell_1_files:
        cell_1_pds.append(pd.read_csv(file_name))

    for file_name in cell_2_files:
        cell_2_pds.append(pd.read_csv(file_name))

    # Combine all the DataFrames into one bigger one per cell
    cell_1 = pd.concat(cell_1_pds)
    cell_2 = pd.concat(cell_2_pds)

    cell_1['time'] = cell_1['time(UT-sec-of-day)'] * 1e-3
    cell_2['time'] = cell_2['time(UT-sec-of-day)'] * 1e-3

    # Insert a column with the appropriate date for each cell
    cell_1.insert(0,'Date', '03/04/2016')
    cell_2.insert(0,'Date', '03/04/2016')


    return cell_1, cell_2

def init_ods():
    file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/Cell1 Analysis 03042016.csv'

    file_name_2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/Cell2 Analysis 03042016.csv'

    # Read in the file
    storm = pd.read_csv(file_name)
    storm2 = pd.read_csv(file_name_2)

    # Combine the date and time columns into a single datetime column
    storm.insert(0, 'DateTime',
                 ['{0} {1}'.format(storm['Date'][i], storm['Time'][i]) for i in
                  range(len(storm))])
    storm2.insert(0, 'DateTime',
                  ['{0} {1}'.format(storm2['Date'][i], storm2['Time'][i]) for i in
                   range(len(storm2))])

    storm['DateTime'] = pd.to_datetime(storm['DateTime'],
                                       format='%m/%d/%y %H:%M:%S.%f')
    storm2['DateTime'] = pd.to_datetime(storm2['DateTime'],
                                        format='%m/%d/%y %H:%M:%S.%f')

    # Convert the values in the duration column to timedelta objects
    storm['Duration(s)'] = pd.to_timedelta(storm['Duration (ms)'], unit='ms')
    storm2['Duration(s)'] = pd.to_timedelta(storm2['Duration (ms)'], unit='ms')

    # Remove unnecessary colums
    _ = storm.pop('Date')
    _ = storm.pop('Time')
    _ = storm.pop('Flash')
    _ = storm.pop('Comments')
    _ = storm.pop('Duration (ms)')

    _ = storm2.pop('Date')
    _ = storm2.pop('Time')
    _ = storm2.pop('Flash')
    _ = storm2.pop('Comments')
    _ = storm2.pop('Duration (ms)')

    return storm, storm2


if __name__ == '__main__':
    cells = init_lma()
    storm_lma_1 = st.Storm(cells[0])
    storm_lma_2 = st.Storm(cells[1])

    cells = init_ods()
    storm_ods_1 = st.Storm(cells[0])
    storm_ods_2 = st.Storm(cells[1])

    storm_ods_1.get_flash_rate(category='IC')
    storm_ods_1.get_flash_rate(category='CG')
    storm_lma_1.plot_all_charge_regions()

    storm_ods_2.get_flash_rate(category='IC')
    storm_ods_2.get_flash_rate(category='CG')
    storm_lma_2.plot_all_charge_regions(show_plot=True)
