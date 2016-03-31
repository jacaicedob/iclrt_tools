#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st

def init_lma():
    # File names for first and second part of storm analysis
    file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-1of2-exported.csv'
    file_name_2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-2of2-exported.csv'

    # Create Pandas objects
    storm_1 = pd.read_csv(file_name)
    storm_2 = pd.read_csv(file_name_2)

    # Insert a column with the appropriate date for each part
    storm_1.insert(0, 'Date', '08/27/2015')
    storm_2.insert(0, 'Date', '08/28/2015')

    # Add 1-day to the seconds of day
    d = datetime.timedelta(days=1).total_seconds()
    storm_2['time(UT-sec-of-day)'] += d

    # Combine both DataFrames into one
    storm = pd.concat([storm_1, storm_2])

    # Create a Series that stores the seconds per day in terms of thousands
    # (for plotting purposes)
    storm['time'] = storm['time(UT-sec-of-day)'] * 1e-3

    return storm


def init_ods():
    file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA Analysis 08272015.csv'

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

    storm_ods.get_flash_rate(category='CG')
    storm_ods.get_flash_rate(category='IC')