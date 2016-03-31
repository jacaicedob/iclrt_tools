#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns

import iclrt_tools.plotting.dfplots as df

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
    storm_2['time(UT-sec-of-day)'] +=  d

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


def get_charge_regions(storm):
    # Generate a DataFrame for all positive charge sources
    positive_charge = storm[storm['charge'] == 3]

    # Generate a DataFrame for all negative charge sources
    negative_charge = storm[storm['charge'] == -3]

    # Generate a DataFrame for all non-determined sources
    other = storm[storm['charge'] == 0]

    return positive_charge, negative_charge, other

def analyze_pos_neg_charge(storm):
    positive_charge, negative_charge, _ = get_charge_regions(storm)

    # Get quick statistics on the positive charge sources
    mean = positive_charge['alt(m)'].mean()
    stdev = positive_charge['alt(m)'].std()
    minn = positive_charge['alt(m)'].min()
    maxx = positive_charge['alt(m)'].max()

    print('Positive charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))

    # Get quick statistics on the negative charge sources
    mean = negative_charge['alt(m)'].mean()
    stdev = negative_charge['alt(m)'].std()
    minn = negative_charge['alt(m)'].min()
    maxx = negative_charge['alt(m)'].max()

    print('Negative charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))

    return positive_charge, negative_charge


def plot_charge_region(storm, charge='positive', hist=True):
    positive_charge, negative_charge, other = get_charge_regions(storm)

    if charge == 'positive':
        charge = positive_charge
    elif charge == 'negative':
        charge = negative_charge
    else:
        charge = other

    # Plot the sources and histogram
    if hist:
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    else:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    if charge['charge'] == 3:
        color = 'r'
    elif charge['charge'] == -3:
        color = 'b'
    else:
        color = 'g'

    charge.plot('time', 'alt(m)', kind='scatter', c=color, lw=0,
                alpha=0.01, ax=ax)

    if hist:
        charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                              color=color, alpha=0.5, bins=1000, lw=0)

        ax2.set_title('Altitude Histrogram')
        ax2.set_xlabel('Number of sources')

    ax.set_title('Positive Charge Sources')
    ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
    ax.set_ylabel('Altitude (m)')

    ax.grid(True)
    ax.set_ylim([0, 16e3])

    if hist:
        return fig, ax, ax2
    else:
        return fig, ax


def plot_all_charge_regions(storm, hist=True):
    positive_charge, negative_charge, _ = get_charge_regions(storm)

    # Plot both charge sources and histogram
    if hist:
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    else:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    positive_charge.plot('time', 'alt(m)', kind='scatter', c='r', lw=0,
                         alpha=0.01, ax=ax)
    negative_charge.plot('time', 'alt(m)', kind='scatter', c='b', lw=0,
                         alpha=0.01, ax=ax)

    # xlims = ax.get_xlim()
    # ax.plot([xlims[0], xlims[1]],
    #         [subset_pos_charge.mean(), subset_pos_charge.mean()],
    #         'g')
    # ax.plot([xlims[0], xlims[1]],
    #         [subset_neg_charge.mean(), subset_neg_charge.mean()],
    #         'g')

    if hist:
        positive_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                       color='r', alpha=0.5, bins=1000, lw=0)
        negative_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                       color='b', alpha=0.5, bins=1000, lw=0)
        ax2.set_title('Altitude Histrogram')
        ax2.set_xlabel('Number of sources')

    ax.set_title('Sources')
    ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
    ax.set_ylabel('Altitude (m)')

    ax.grid(True)
    ax.set_ylim([0, 16e3])

    if hist:
        return fig, ax, ax2
    else:
        return fig, ax


def analyze_subset(storm, sod_start, sod_end, plot=True):
    # Analyze a subset of the entire storm
    subset = storm[storm['time(UT-sec-of-day)'] < sod_end]
    subset = subset[subset['time(UT-sec-of-day)'] > sod_start]

    plot_all_charge_regions(subset)


def plot_interval(storm, interval=5):
    # Plot both charge regions and histrogram at a certain interval (in minutes).
    t_increment = interval*60  # seconds

    positive_charge, negative_charge, _ = get_charge_regions(storm)

    start_time = positive_charge['time(UT-sec-of-day)'].min()
    end_time = start_time + t_increment

    while start_time < positive_charge['time(UT-sec-of-day)'].max():
        subset = storm[storm['time(UT-sec-of-day)'] < end_time]
        subset = subset[subset['time(UT-sec-of-day)'] > start_time]

        subset_pos_charge = subset[subset['charge'] == 3]
        subset_neg_charge = subset[subset['charge'] == -3]

        try:
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)

            subset_pos_charge.plot('time', 'alt(m)',
                                   kind='scatter', c='r', lw=0, alpha=0.01,
                                   ax=ax)
            subset_neg_charge.plot('time', 'alt(m)',
                                   kind='scatter', c='b', lw=0, ax=ax,
                                   alpha=0.01)

            subset_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                             color='r', alpha=0.5, bins=1000, lw=0)
            subset_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                             color='b', alpha=0.5, bins=1000, lw=0)


            ax.set_title('Sources')
            ax2.set_title('Altitude Histrogram')

            ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
            ax2.set_xlabel('Number of sources')

            ax.set_ylabel('Altitude (m)')

            ax.grid(True)
            ax.set_ylim([0, 16e3])

            fig.savefig('./storm-08-27-2015_%d.png' % start_time,
                        format='png', dpi=300)
        except TypeError as e:
            pass

        start_time = end_time
        end_time += t_increment


def get_flash_rate(storm, interval=5, category='all'):
    original = storm

    # Calculate flash rate every 5 minutes
    t_interval = datetime.timedelta(minutes=interval)
    t_start = storm['DateTime'].min()
    t_end = t_start + t_interval

    if category.lower() == 'ic':
        storm = storm[storm['Type'] == 'IC']

    elif category.lower() == '-cg' or category.lower() == 'cg':
        storm1 = storm[storm['Type'] == '-CG']
        storm2 = storm[storm['Type'] == 'CG']

        storm = pd.concat([storm1, storm2])

    print('\nFlash rate for {0} flashes (interval: {1} minutes):'.format(
        category.upper(), interval))
    print('-' * 50)

    while t_start < storm['DateTime'].max():
        temp = storm[storm['DateTime'] < t_end]
        temp = temp[temp['DateTime'] >= t_start]
        start = datetime.datetime.strftime(t_start, '%H:%M:%S.%f')
        end = datetime.datetime.strftime(t_end, '%H:%M:%S.%f')

        rate = (len(temp) / t_interval.total_seconds()) * 60
        print('Flash rate between {0} -- {1} is {2:0.2f} per min'.format(start,
                                                                         end,
                                                                         rate))
        t_start = t_end
        t_end += t_interval

    # Entire storm flash rate
    rate = len(storm) / (storm['DateTime'].max() -
                         storm['DateTime'].min()).total_seconds() * 60



    print('\nNumber of {0}s: {1}/{2} total ({3:0.2f}%)'.format(category.upper(),
                                                len(storm), len(original),
                                                len(storm) / len(original) * 100))
    print('Average {0} rate of entire storm: {1:0.2f} per minute'.format(category.upper(), rate))

if __name__ == '__main__':
    storm_lma = init_lma()
    storm_ods = init_ods()
    # fig, ax, ax2 = plot_all_charge_regions(storm)
    # p = df.Plot(fig, ax)
    # p.plot()

    get_flash_rate(storm_ods, category='CG')
    get_flash_rate(storm_ods, category='IC')

    plt.show()