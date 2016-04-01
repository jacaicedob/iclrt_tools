#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import seaborn as sns

import iclrt_tools.plotting.dfplots as df


class Storm(object):
    """
    An object for analyzing data exported from the xlma software using the
    Pandas module.

        Parameters:
        -----------
        storm: Pandas DataFrame
            Contains the entire data set merged from files.

        Attributes:
        -----------
        storm: Pandas DataFrame
            Contains the entire data set merged from files.
        positive_charge: Pandas DataFrame
            Contains the data set for the sources classified as positive charge.
        negative_charge: Pandas DataFrame
            Contains the data set for the sources classified as negative charge.
        other: Pandas DataFrame
            Contains the data set for the sources without classification.

    """

    def __init__(self, storm):
        """ Initialize the object. """
        self.storm = storm
        self.positive_charge = None
        self.negative_charge = None
        self.other = None

    @classmethod
    def from_lma_files(cls, files, dates):
        """ Initialize the object from files and dates """
        storm = cls._parse_lma_files(files, dates)
        return cls(storm)

    @classmethod
    def from_ods_file(cls, file):
        """ Initialize the object from files and dates """
        storm = cls._parse_ods_file(file)
        return cls(storm)

    @staticmethod
    def _parse_lma_files(files, dates):

        pds = []

        # Read in the files
        for i, f in enumerate(files):
            pds.append(pd.read_csv(f))

        # Add a Series to each DataFrame containing the time of each source
        # in datetime form
        for i, p in enumerate(pds):
            if len(dates) > 1:
                try:
                    date = datetime.datetime.strptime(dates[i], '%m/%d/%y')
                except ValueError:
                    date = datetime.datetime.strptime(dates[i], '%m/%d/%Y')

                series = [date + datetime.timedelta(seconds=entry) for entry
                          in p['time(UT-sec-of-day)']]

                p.insert(0, 'DateTime', series)
                p['DateTime'] = pd.to_datetime(p['DateTime'])

            else:
                try:
                    date = datetime.datetime.strptime(dates[0], '%m/%d/%y')
                except ValueError:
                    date = datetime.datetime.strptime(dates[0], '%m/%d/%Y')

                series = [date + datetime.timedelta(seconds=entry) for entry
                          in p['time(UT-sec-of-day)']]

                p.insert(0, 'DateTime', series)
                p['DateTime'] = pd.to_datetime(p['DateTime'])

        # Correct the flash numbers so that there are no duplicates
        for i in range(len(pds) - 1):
            max_flash_number = pds[i]['flash-number'].max()

            pds[i+1]['flash-number'] += max_flash_number

        # Make the final Pandas DataFrame
        if len(pds) > 1:
            storm = pd.concat(pds)
        else:
            storm = pds[0]

        _ = storm.pop('#-of-stations-contributed')
        _ = storm.pop('reduced-chi^2')
        _ = storm.pop('time(UT-sec-of-day)')
        storm.set_index('DateTime', inplace=True)
        return storm

    @staticmethod
    def _parse_ods_file(file):

        storm = pd.read_csv(file)

        # Combine the date and time columns into a single datetime column
        storm.insert(0, 'DateTime',
                     ['{0} {1}'.format(storm['Date'][i], storm['Time'][i])
                      for i in
                      range(len(storm))])
        storm['DateTime'] = pd.to_datetime(storm['DateTime'],
                                           format='%m/%d/%y %H:%M:%S.%f')

        # Convert the values in the duration column to timedelta objects
        storm['Duration(s)'] = pd.to_timedelta(storm['Duration (ms)'],
                                               unit='ms')

        # Remove unnecessary colums
        _ = storm.pop('Date')
        _ = storm.pop('Time')
        _ = storm.pop('Flash')
        _ = storm.pop('Comments')
        _ = storm.pop('Duration (ms)')

        storm['Initiation Height (km)'] = pd.to_numeric(
            storm['Initiation Height (km)'], errors='coerce')

        return storm

    def get_charge_regions(self):
        # Generate a DataFrame for all positive charge sources
        self.positive_charge = self.storm[self.storm['charge'] == 3]
    
        # Generate a DataFrame for all negative charge sources
        self.negative_charge = self.storm[self.storm['charge'] == -3]
    
        # Generate a DataFrame for all non-determined sources
        self.other = self.storm[self.storm['charge'] == 0]
    
        return self.positive_charge, self.negative_charge, self.other
    
    def analyze_pos_neg_charge(self):
        positive_charge, negative_charge, _ = self.get_charge_regions()
    
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

    def plot_charge_region(self, charge='positive', hist=True,
                           show_plot=False):
        positive_charge, negative_charge, other = self.get_charge_regions()
    
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
    
        if charge['charge'].unique() == 3:
            color = 'r'
        elif charge['charge'].unique() == -3:
            color = 'b'
        else:
            color = 'g'
    
        charge.plot(y='alt(m)', style='.', c=color, lw=0, alpha=0.01,
                    ax=ax, legend=False)
    
        if hist:
            charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                  color=color, alpha=0.5, bins=1000, lw=0)
    
            ax2.set_title('Altitude Histrogram')
            ax2.set_xlabel('Number of sources')
    
        ax.set_title('Positive Charge Sources')
        ax.set_xlabel(r'Time (sec of day) ')
        ax.set_ylabel('Altitude (m)')
    
        ax.grid(True)
        ax.set_ylim([0, 16e3])

        if show_plot:
            plt.show()

        if hist:
            return fig, ax, ax2
        else:
            return fig, ax
    
    def plot_all_charge_regions(self, hist=True, show_plot=False):
        positive_charge, negative_charge, _ = self.get_charge_regions()
    
        # Plot both charge sources and histogram
        if hist:
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
        else:
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
        positive_charge.plot(y='alt(m)', style='.', c='r', lw=0,
                             alpha=0.01, ax=ax, legend=False)
        negative_charge.plot(y='alt(m)', style='.', c='b', lw=0,
                             alpha=0.01, ax=ax, legend=False)
    
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
        ax.set_xlabel(r'Time (sec of day) ')
        ax.set_ylabel('Altitude (m)')
    
        ax.grid(True)
        ax.set_ylim([0, 16e3])

        if show_plot:
            plt.show()

        if hist:
            return fig, ax, ax2
        else:
            return fig, ax

    def analyze_subset(self, start, end, plot=True):
        # Analyze a subset of the entire self.storm
        subset = self.storm[start:end]
        # print(subset.index)

        subset = Storm(subset)
        # print(subset.storm.index)
        subset.plot_all_charge_regions(show_plot=plot)

    def plot_interval(self, path='./', interval=5):
        # Plot both charge regions and histrogram at a certain
        # interval (in minutes).
        t_increment = datetime.timedelta(seconds=interval*60)
    
        positive_charge, negative_charge, _ = self.get_charge_regions()
    
        start_time = positive_charge.index.min()
        end_time = start_time + t_increment
    
        while start_time < positive_charge.index.max():
            ind_start = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S.%f')
            ind_end = datetime.datetime.strftime(end_time,
                                                   '%Y-%m-%d %H:%M:%S.%f')
            subset = self.storm[ind_start:ind_end]
            subset_pos_charge = subset[subset['charge'] == 3]
            subset_neg_charge = subset[subset['charge'] == -3]
    
            try:
                fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    
                subset_pos_charge.plot(y='alt(m)',
                                       style='.', c='r', lw=0, alpha=0.01,
                                       ax=ax, legend=False)
                subset_neg_charge.plot(y='alt(m)',
                                       style='.', c='b', lw=0, ax=ax,
                                       alpha=0.01, legend=False)
    
                subset_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                                 color='r', alpha=0.5, bins=1000, lw=0)
                subset_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                                 color='b', alpha=0.5, bins=1000, lw=0)
    
    
                ax.set_title('Sources')
                ax2.set_title('Altitude Histrogram')
    
                ax.set_xlabel(r'Time')
                ax2.set_xlabel('Number of sources')
    
                ax.set_ylabel('Altitude (m)')
    
                ax.grid(True)
                ax.set_ylim([0, 16e3])

                file_name = path
                file_name += 'storm_%s.png' % datetime.datetime.strftime(start_time, '%Y%m%d-%H%M%S')

                # print(file_name)
                # plt.show()
                fig.savefig(file_name, format='png', dpi=300)
            except TypeError as e:
                pass
    
            start_time = end_time
            end_time += t_increment

    def get_flash_rate(self, interval=5, category='all'):
        original = self.storm
    
        # Calculate flash rate every 5 minutes
        t_interval = datetime.timedelta(minutes=interval)
        t_start = self.storm['DateTime'].min()
        t_end = t_start + t_interval
    
        if category.lower() == 'ic':
            temp_storm = self.storm[self.storm['Type'] == 'IC']
    
        elif category.lower() == '-cg' or category.lower() == 'cg':
            storm1 = self.storm[self.storm['Type'] == '-CG']
            storm2 = self.storm[self.storm['Type'] == 'CG']

            temp_storm = pd.concat([storm1, storm2])
    
        print('\nFlash rate for {0} flashes (interval: {1} minutes):'.format(
            category.upper(), interval))
        print('-' * 50)
    
        while t_start < self.storm['DateTime'].max():
            temp = temp_storm[self.storm['DateTime'] < t_end]
            temp = temp[temp['DateTime'] >= t_start]

            start = datetime.datetime.strftime(t_start, '%H:%M:%S.%f')
            end = datetime.datetime.strftime(t_end, '%H:%M:%S.%f')
    
            rate = (len(temp) / t_interval.total_seconds()) * 60
            t_start = t_end
            print('Flash rate between {0} -- {1} is {2:0.2f} '
                  'per min ({3} flashes total)'.format(start, end, rate,
                                                       len(temp)))
            t_end += t_interval
    
        # Entire self.storm flash rate
        r = self.storm['DateTime'].max() - self.storm['DateTime'].min()
        rate = len(temp_storm) / r.total_seconds() * 60

        print('\nNumber of {0}s: {1}/{2} total '
              '({3:0.2f}%)'.format(category.upper(), len(temp_storm),
                                   len(original),
                                   len(temp_storm) / len(original) * 100))

        print('Average {0} rate of entire self.storm: {1:0.2f} '
              'per minute'.format(category.upper(), rate))

    def get_storm_summary(self, charge=None, flash_types=None):
        try:

            if flash_types is None:
                types = self.storm['Type'].unique()
            else:
                types = flash_types

            for t in types:
                storm = self.storm[self.storm['Type'] == t]
                s = '\n'
                s += '{0} : {1}\n'.format(t, len(storm))

                print(s)
                print(storm.describe())

        except KeyError:
            print("LMA File: Charge {0}".format(charge.upper()))

            if charge is None:
                storm = self.storm
            elif charge == 'positive':
                storm = self.storm[self.storm['charge'] == 3]
            elif charge == 'negative':
                storm = self.storm[self.storm['charge'] == -3]
            elif charge == 'other':
                storm = self.storm[self.storm['charge'] == 0]

            print(storm.describe())
