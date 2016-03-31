#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns

import iclrt_tools.plotting.dfplots as df


class Storm(object):

    def __init__(self, storm):
        self.storm = storm
        self.positive_charge = None
        self.negative_charge = None
        self.other = None

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

        if show_plot:
            plt.show()

        if hist:
            return fig, ax, ax2
        else:
            return fig, ax

    def analyze_subset(self, sod_start, sod_end, plot=True):
        # Analyze a subset of the entire self.storm
        subset = self.storm[self.storm['time(UT-sec-of-day)'] < sod_end]
        subset = subset[subset['time(UT-sec-of-day)'] > sod_start]

        subset = Storm(subset)
        subset.plot_all_charge_regions()

    def plot_interval(self, interval=5):
        # Plot both charge regions and histrogram at a certain interval (in minutes).
        t_increment = interval*60  # seconds
    
        positive_charge, negative_charge, _ = self.get_charge_regions()
    
        start_time = positive_charge['time(UT-sec-of-day)'].min()
        end_time = start_time + t_increment
    
        while start_time < positive_charge['time(UT-sec-of-day)'].max():
            subset = self.storm[self.storm['time(UT-sec-of-day)'] < end_time]
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
    
                fig.savefig('./self.storm-08-27-2015_%d.png' % start_time,
                            format='png', dpi=300)
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