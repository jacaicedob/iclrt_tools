#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pickle
import seaborn as sns
import os
import sys

import iclrt_tools.plotting.dfplots as df
import iclrt_tools.lat_lon.lat_lon as ll

# sns.set_context('talk', font_scale=2.0)


class Storm(object):
    """
    A class structure to instantiate analyzed LMA data from an Excel or
    LibreOffice generated .csv file and from xlma exported .dat files.

        Parameters:
        -----------
            storm: Pandas DataFrame (optional)
                Contains the entire data set.

        Attributes:
        -----------
            storm: Pandas DataFrame
                Contains the entire data set.
    """

    def __init__(self, storm=None):
        self.storm = storm

    def convert_latlon_to_km(self, x_loc=None, y_loc=None):
        """
        Convert the lat, lon entries into distance from the ICLRT in a
        Cartesian plane, just like the xlma software does. Append two Series
        to the current DataFrame to hold the x and y values just calculated.

        Parameters:
        -----------
            x_loc: int
                Column number (base 0) where to insert the x result
            y_loc: int
                Column number (base 0) where to insert the y result
        """

        gnd_launcher_latlon = [29.9429917, -82.0332305, 0]  # Gnd Launcher
        center = ll.Location(gnd_launcher_latlon[0],
                             gnd_launcher_latlon[1])

        # Convert to WGS-84
        center_xyz = center.xyz_transform()

        results = dict()
        results['DateTime'] = []
        results['x (m)'] = []
        results['y (m)'] = []

        count = 0
        total = len(self.storm)

        print('Total Entries: {0}'.format(total))
        start = datetime.datetime.now()

        for i, s in self.storm.iterrows():
            print('Converting... {0:0.2f}%'.format(count / total * 100),
                  end='\r')
            # Convert to WGS-84
            location = ll.Location(s['lat'], s['lon'])
            xyz = location.xyz_transform()

            # Center around "center"
            x = xyz[0] - center_xyz[0]
            y = xyz[1] - center_xyz[1]
            z = xyz[2] - center_xyz[2]

            # Apply rotations to correct orientations
            # This was ported from the xlma IDL code from file lonlat_to_xy.pro

            lonr = -center.lonr
            colat = -(np.pi / 2 - center.latr)

            rot_lon = np.array(([np.cos(lonr), -np.sin(lonr), 0],
                                [np.sin(lonr), np.cos(lonr), 0],
                                [0, 0, 1]))

            rot_lat = np.array(([1, 0, 0],
                                [0, np.cos(colat), -np.sin(colat)],
                                [0, np.sin(colat), np.cos(colat)]))

            rot_z90 = np.array(([0, 1, 0],
                                [-1, 0, 0],
                                [0, 0, 1]))

            temp = np.array((x, y, z))  # np.array(([x], [y], [z]))

            ssl = np.dot(temp.T, rot_lon.T).T
            ssl = np.dot(ssl.T, rot_z90.T).T
            ssl = np.dot(ssl.T, rot_lat.T).T

            x, y, z = ssl[0], ssl[1], ssl[2]

            results['DateTime'].append(i)
            results['x (m)'].append(x)
            results['y (m)'].append(y)

            count += 1

        end = datetime.datetime.now()
        print('Conversion time: {0}\n'.format(end - start))

        # Insert the x result into the DataFrame
        x_series = pd.Series(results['x (m)'], index=results['DateTime'])

        if x_loc is None:
            x_loc = len(self.storm.columns)

        self.storm.insert(x_loc, 'x (m)', x_series)

        # Insert the y result into the DataFrame
        y_series = pd.Series(results['y (m)'], index=results['DateTime'])

        if y_loc is None:
            y_loc = len(self.storm.columns)

        self.storm.insert(y_loc, 'y (m)', y_series)

    def from_pickle(self, file):
        """ Initialize the object from a save pickle. """

        tmp_dict = pickle.load(open(file, 'rb'))

        self.__dict__.update(tmp_dict)


class StormLMA(Storm):
    """
    An object for analyzing data exported from the xlma software using the
    Pandas module.

        Parameters:
        -----------
        storm: Pandas DataFrame (optional)
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
        nldn_detections: dict
            Dictionary containing the detection data

    """

    def __init__(self, storm=None):
        """ Initialize the object. """

        super(StormLMA, self).__init__(storm)
        self.positive_charge = None
        self.negative_charge = None
        self.other = None
        self.nldn_detections = None

    @staticmethod
    def _calculate_histogram(data_series):
        """ Compute the histogram of a Series and return the bin centers. """

        # Extract data from DataSeries into a np array
        data = np.array(data_series['alt(m)'].dropna())

        # Calculate histogram of the data and find the bin centers
        hist, bin_edges = np.histogram(data, bins=1000)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Return the altitude (bin_center) of the largest value
        # in the histogram
        return bin_centers[np.argmax(hist)]

    @staticmethod
    def _parse_lma_files(files, dates):
        """ Parse the LMA .dat files to generate the DataFrame. """

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

        # Remove all flash-numbers that are == -1
        for i in range(len(pds)):
            row_index = pds[i][pds[i]['flash-number'] != -1].index
            pds[i] = pds[i].loc[row_index]

            # print(-1 in pds[i]['flash-number'])

        # Correct the flash numbers so that there are no duplicates
        for i in range(len(pds) - 1):
            # Get the largest flash number of the current file
            max_flash_number = pds[i]['flash-number'].max() + 1

            # Apply the offset to the next file
            pds[i + 1]['flash-number'] += max_flash_number

        # Make the final Pandas DataFrame
        if len(pds) > 1:
            storm = pd.concat(pds, ignore_index=True)
        else:
            storm = pds[0]

        # _ = storm.pop('#-of-stations-contributed')
        # _ = storm.pop('reduced-chi^2')
        # _ = storm.pop('time(UT-sec-of-day)')
        storm.set_index('DateTime', inplace=True)
        return storm

    def analyze_pos_neg_charge(self):
        """ Analyze the positive and negative sources. """

        positive_charge, negative_charge, _ = self.get_charge_regions()

        # Get quick statistics on the positive charge sources
        mean = positive_charge['alt(m)'].mean()
        stdev = positive_charge['alt(m)'].std()
        minn = positive_charge['alt(m)'].min()
        maxx = positive_charge['alt(m)'].max()

        print(
            'Positive charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(
                mean, stdev, minn, maxx))

        # Get quick statistics on the negative charge sources
        mean = negative_charge['alt(m)'].mean()
        stdev = negative_charge['alt(m)'].std()
        minn = negative_charge['alt(m)'].min()
        maxx = negative_charge['alt(m)'].max()

        print(
            'Negative charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(
                mean, stdev, minn, maxx))

        return positive_charge, negative_charge

    def analyze_subset(self, start, end, plot=True):
        """ Analyze the data between start and end. """

        # Analyze a subset of the entire self.storm
        subset = self.storm.loc[start:end]
        # print(subset.index)

        subset = Storm(subset)
        # print(subset.storm.index)
        subset.plot_all_charge_regions(show_plot=plot)

    def calculate_nldn_efficiency(self, nldn_file):
        """
        Calculate the efficiency of NLDN by correlating the NLDN detected
        flashes with the LMA detected flashes. Save the result as a
        class attribute self.nldn_detections.

        Parameters:
        -----------
        nldn_file: str
            File path to the NLDN file.

        """

        # Read in file
        nldn = pd.read_csv(nldn_file, sep=' ',
                           names=['Date', 'Time', 'lat', 'lon', 'kA', 'Type',
                                  'Mult', 'Dummy', 'Dummy2'])

        # Convert dates to datetime and set the index of the DataFrame
        nldn.insert(0, 'DateTime',
                    ['{0} {1}'.format(nldn['Date'][i], nldn['Time'][i])
                     for i in
                     range(len(nldn))])
        nldn['DateTime'] = pd.to_datetime(nldn['DateTime'],
                                          format='%m/%d/%y %H:%M:%S.%f')
        nldn.set_index('DateTime', inplace=True)

        # Remove unwanted columns
        _ = nldn.pop('Date')
        _ = nldn.pop('Time')
        _ = nldn.pop('Dummy')
        _ = nldn.pop('Dummy2')

        # Limit the NLDN times to the storm times
        start_ind = self.storm.index.min()
        end_ind = self.storm.index.max()
        nldn = nldn.loc[start_ind:end_ind]

        # Setup the container for the results data
        self.nldn_detections = dict()
        self.nldn_detections['flash-number'] = []
        self.nldn_detections['DateTime'] = []
        self.nldn_detections['lat'] = []
        self.nldn_detections['lon'] = []
        self.nldn_detections['Type'] = []
        self.nldn_detections['Mult'] = []
        self.nldn_detections['kA'] = []

        temp = self.storm[self.storm['charge'] != 0]
        numbers = temp['flash-number'].unique()

        # Start the computation of detected NLDN flashes
        count = 1
        total = len(nldn.index) * len(numbers)

        print('Total Iterations: {0}'.format(total))
        start = datetime.datetime.now()
        for i in nldn.index:
            # # Ignore the times in the file that are outside the range of
            # # the analyzed storm.
            # if not (self.storm.index.min() <= i <= self.storm.index.max()):
            #     continue

            for flash_number in numbers:
                count += 1
                flash = self.storm[self.storm['flash-number'] == flash_number]

                if flash.index.min() <= i <= flash.index.max():
                    self.nldn_detections['flash-number'].append(flash_number)
                    self.nldn_detections['DateTime'].append(i)
                    self.nldn_detections['lat'].append(nldn.loc[i]['lat'])
                    self.nldn_detections['lon'].append(nldn.loc[i]['lon'])
                    self.nldn_detections['Type'].append(nldn.loc[i]['Type'])
                    self.nldn_detections['Mult'].append(nldn.loc[i]['Mult'])
                    self.nldn_detections['kA'].append(nldn.loc[i]['kA'])

                print('Analyzing... {0:0.2f}%'.format(count / total * 100),
                      end='\r')
        # print()
        end = datetime.datetime.now()
        print('Analisis time: {0}\n'.format(end - start))
        print('NLDN detected flashes: {0}'.format(len(nldn)))
        print('LMA analyzed flashes: {0}'.format(len(numbers)))
        print('Uncorrelated detection efficiency: {0}'.format(
            len(nldn) / len(numbers)))
        print(
            'Correlated NLDN detections with analyzed LMA flashes: {0}'.format(
                len(self.nldn_detections['flash-number'])))
        print('Correlated detection efficiency: {0}'.format(
            len(self.nldn_detections['flash-number']) / len(numbers)))

    @classmethod
    def from_lma_files(cls, files, dates):
        """ Initialize the object from files and dates """

        storm = cls._parse_lma_files(files, dates)
        return cls(storm)

    def get_charge_regions(self):
        """ Return DataFrames corresponding to each charge region. """

        # Generate a DataFrame for all positive charge sources
        self.positive_charge = self.storm[self.storm['charge'] == 3]
    
        # Generate a DataFrame for all negative charge sources
        self.negative_charge = self.storm[self.storm['charge'] == -3]
    
        # Generate a DataFrame for all non-determined sources
        self.other = self.storm[self.storm['charge'] == 0]
    
        return self.positive_charge, self.negative_charge, self.other

    def get_sources_from_flash_number(self, flash_number=None):
        """
            Get the LMA sources for flash_number.

            Parameters
            ----------
                flash_number: int
                    Flash number to get.

            Returns
            -------
                subset : DataFrame
                    DataFrame with sources.
            """

        if type(flash_number) == np.int64 or type(flash_number) == int:
            subset = self.storm[self.storm['flash-number'] == flash_number]
        else:
            temp = []
            for n in flash_number:
                temp.append(self.storm[self.storm['flash-number'] == n])

            subset = pd.concat(temp)

        subset.sort_index(inplace=True)

        return subset

    def get_flash_plotter_from_number(self, flash_number=None):
        """
        Get the LMA sources for flash_number.

        Parameters
        ----------
            flash_number: int
                Flash number to get.

        Returns
        -------
            p : LMAPlotter
                Plotter object.
        """

        # Generate the header contents for the temporary .dat file
        # that will contain the LMA sources for one flash.
        d = datetime.datetime.strftime(self.storm.index[0], '%m/%d/%Y')
        date = 'Data start time: {0}'.format(d)
        center = 'Coordinate center (lat,lon,alt): 29.9429917 -82.0332305 0.00'
        data_str = '*** data ***'

        # Temporary file to store the LMA sources of a single flash
        temp_file = './temp.dat'

        if type(flash_number) == np.int64 or type(flash_number) == int:
            subset = self.storm[self.storm['flash-number'] == flash_number]
        else:
            temp = []
            for n in flash_number:
                temp.append(self.storm[self.storm['flash-number'] == n])

            subset = pd.concat(temp)

        subset.reset_index(inplace=True)

        # Open the temporary LMA .dat file and write the header.
        with open(temp_file, 'w') as f:
            f.write(date + '\n')
            f.write(center + '\n')
            f.write(data_str + '\n')

            # Go through each source and write the information out to the
            # temporary .dat file
            for ind in subset.index:
                data = ' '.join(
                    [str(subset['time(UT-sec-of-day)'][ind]),
                     str(subset['lat'][ind]),
                     str(subset['lon'][ind]),
                     str(subset['alt(m)'][ind]),
                     str(subset['reduced-chi^2'][ind]),
                     str(subset['P(dBW)'][ind]),
                     str(subset['mask'][ind])])

                data += '\n'

                f.write(data)

        # sys.exit(1)
        # Create the LMAPlotter object and run the measure_area() function
        p = df.LMAPlotter(temp_file)

        # Delete the temporary .dat file
        if os.path.isfile(temp_file):
            os.remove(temp_file)

        return p

    def get_flash_plotter_from_time(self, start=datetime.datetime.now(),
                                    end=datetime.datetime.now()):
        """
        Get the LMA sources between start and end.

        Parameters
        ----------
            start: datetime
                Datetime object that specifies the start of the flash.
            end: datetime
                Datetime object that specifies the start of the flash.

        Returns
        -------
            p : LMAPlotter
                Plotter object.
        """

        subset = self.storm.loc[start:end]

        # Count the number of sources corresponding to each flash
        # number in the subset
        counts = subset['flash-number'].value_counts()

        # Get the flash number with the most sources in this time period
        number = counts[counts == counts.max()].index[0]

        # Generate the header contents for the temporary .dat file
        # that will contain the LMA sources for one flash.
        d = datetime.datetime.strftime(self.storm.index[0], '%m/%d/%Y')
        date = 'Data start time: {0}'.format(d)
        center = 'Coordinate center (lat,lon,alt): 29.9429917 -82.0332305 0.00'
        data_str = '*** data ***'

        # Temporary file to store the LMA sources of a single flash
        temp_file = './temp.dat'

        subset = self.storm[self.storm['flash-number'] == number]
        subset.reset_index(inplace=True)

        # Open the temporary LMA .dat file and write the header.
        with open(temp_file, 'w') as f:
            f.write(date + '\n')
            f.write(center + '\n')
            f.write(data_str + '\n')

            # Go through each source and write the information out to the
            # temporary .dat file
            for ind in subset.index:
                data = ' '.join(
                    [str(subset['time(UT-sec-of-day)'][ind]),
                     str(subset['lat'][ind]),
                     str(subset['lon'][ind]),
                     str(subset['alt(m)'][ind]),
                     str(subset['reduced-chi^2'][ind]),
                     str(subset['P(dBW)'][ind]),
                     str(subset['mask'][ind])])

                data += '\n'

                f.write(data)

        # sys.exit(1)
        # Create the LMAPlotter object and run the measure_area() function
        p = df.LMAPlotter(temp_file)

        # Delete the temporary .dat file
        if os.path.isfile(temp_file):
            os.remove(temp_file)

        return p

    def measure_flash_area(self, file_name=None):
        """
        Measures the area (graphically) of all flashes in a storm by
        generating a temporary .dat file to hold the source data for a
        particular flash and instantiating a dfplots.LMAPlotter object.
        It saves the area retults to the specified file_name as comma
        separated values.

        Parameters
        ----------
            file_name: str
                File used to save the area results.

        """
        if file_name is None:
            file = './test.csv'
        else:
            file = file_name

        # Get all charge classified sources
        all_charge = self.storm[self.storm['charge'] != 0]

        # Get all the flash numbers in the data
        numbers = all_charge['flash-number'].unique()
        # print(numbers)

        # Generate the header contents for the temporary .dat file
        # that will contain the LMA sources for one flash.
        d = datetime.datetime.strftime(self.storm.index[0], '%m/%d/%Y')
        date = 'Data start time: {0}'.format(d)
        center = 'Coordinate center (lat,lon,alt): 29.9429917 -82.0332305 0.00'
        data_str = '*** data ***'

        # Temporary file to store the LMA sources of a single flash
        temp_file = './temp.dat'

        # Open the file and find the last flash number that was saved to
        # resume from there.
        last = None
        try:
            with open(file, 'r') as f:
                for last in (line for line in f if line.rstrip('\n')):
                    pass
        except FileNotFoundError:
            pass

        if last is None:
            index = 0
        else:
            index = np.where(numbers == int(last.split(',')[1]))[0][0] + 1

        # Start the iteration over the unique flash numbers and populate the
        # temporary LMA .dat file to create an LMAPlotter object and use
        # the measure_area() function to graphically measure the flash areas
        # of all flashes.
        for flash_number in numbers[index:]:
            # Open the file that will store the area calculations
            with open(file, 'a') as ff:

                # Select all the sources (classified and unclassified) for each
                # flash number.
                flash = self.storm[self.storm['flash-number'] == flash_number]
                flash.reset_index(inplace=True)

                # Open the temporary LMA .dat file and write the header.
                with open(temp_file, 'w') as f:
                    f.write(date + '\n')
                    f.write(center + '\n')
                    f.write(data_str + '\n')

                    # Go through each source and write the information out to the
                    # temporary .dat file
                    for ind in flash.index:
                        data = ' '.join(
                            [str(flash['time(UT-sec-of-day)'][ind]),
                             str(flash['lat'][ind]),
                             str(flash['lon'][ind]),
                             str(flash['alt(m)'][ind]),
                             str(flash['reduced-chi^2'][ind]),
                             str(flash['P(dBW)'][ind]),
                             str(flash['mask'][ind])])

                        data += '\n'

                        f.write(data)

                # sys.exit(1)
                # Create the LMAPlotter object and run the measure_area() function
                p = df.LMAPlotter(temp_file)

                fig, ax = plt.subplots(1, 1)
                p.measure_area(ax)
                plt.show()

                # Write the results to file and close the file
                ff.write(
                    ','.join([datetime.datetime.strftime(p.plot_data['t'][0],
                                                         '%m/%d/%Y %H:%M:%S.%f'),
                              str(flash_number), str(p.lasso.area)]))
                ff.write('\n')

        # Delete the temporary .dat file
        if os.path.isfile(temp_file):
            os.remove(temp_file)

    def plot_charge_region(self, charge='positive', hist=True,
                           show_plot=False):
        """
        Plot the LMA sources of a charge region. The histogram can be plotted
        also.

        Parameters
        ----------
            charge: str (optional)
                The charge to be plotter, i.e., positive or negative.
            hist: bool
                Boolean flag to include the histogram in the plot.
            show_plot: bool
                Boolean flag to show the plot.

        Returns
        -------
            fig: matplotlib.Figure
                Figure instance of plot
            ax: matplotlib.Axes
                Axis instance of plot
            ax2: matplotlib.Axes
                Axis instance of histogram (only when hist is True)
        """

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
            title = 'Positive Charge Sources'
        elif charge['charge'].unique() == -3:
            color = 'b'
            title = 'Negative Charge Sources'
        else:
            color = 'g'
            title = 'Other Sources'
    
        charge.plot(y='alt(m)', style='.', c=color, lw=0, alpha=0.01,
                    ax=ax, legend=False)
    
        if hist:
            charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                  color=color, alpha=0.5, bins=1000, lw=0)
    
            ax2.set_title('Altitude Histrogram')
            ax2.set_xlabel('Number of sources')
    
        ax.set_title(title)
        ax.set_xlabel(r'Time')
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
        """
        Plot both charge regions together. The source histograms can also
        be plotted. The default is to not show the plot.

        Parameters
        ----------
            hist: bool (optional)
                Boolean flag to show the histogram in the plot
            show_plot: bool (optional)
                Boolean flag to show the plot

        Returns
        -------
            fig: matplotlib.Figure
                Figure instance of plot
            ax: matplotlib.Axes
                Axis instance of plot
            ax2: matplotlib.Axes
                Axis instance of histogram (only when hist is True)

        """

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
        ax.set_xlabel(r'Time')
        ax.set_ylabel('Altitude (m)')
    
        ax.grid(True)
        ax.set_ylim([0, 16e3])

        if show_plot:
            plt.show()

        if hist:
            return fig, ax, ax2
        else:
            return fig, ax

    def plot_intervals(self, interval=5, hist=True,
                       savefigs=False, path='./',):
        """
        Generate plots of the charge regions and their histograms starting
        at the time of the earliest positive source and every 'interval'
        minutes. The plots can be saved if the user wants.

            Parameters:
            -----------
            interval: int (optional)
                Time interval in minutes.
            hist: bool (optional)
                Boolean flag to plot the histogram.
            savefigs: bool (optional)
                Boolean flag to save the plots.
            path: str (optional)
                Path onto which the plots will be saved.

        """

        # Plot both charge regions and histogram at a certain
        # interval (in minutes).
        t_increment = datetime.timedelta(seconds=interval*60)
    
        positive_charge, negative_charge, _ = self.get_charge_regions()
    
        start_time = positive_charge.index.min()
        end_time = start_time + t_increment

        # These lists will hold the altitude of the peak of each histogram as
        # well as the time interval when they occur
        t_peaks = []
        pos_peaks = []
        neg_peaks = []
    
        while start_time < positive_charge.index.max():
            ind_start = datetime.datetime.strftime(start_time,
                                                   '%Y-%m-%d %H:%M:%S.%f')
            ind_end = datetime.datetime.strftime(end_time,
                                                 '%Y-%m-%d %H:%M:%S.%f')

            subset = self.storm.loc[start_time:end_time]  #[ind_start, ind_end]
            subset_pos_charge = subset[subset['charge'] == 3]
            subset_neg_charge = subset[subset['charge'] == -3]

            try:
                if hist:
                    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6),
                                                  sharey=True)
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
                subset_pos_charge.plot(y='alt(m)', style='.', c='r', lw=0,
                                       alpha=0.01, ax=ax, legend=False)
                subset_neg_charge.plot(y='alt(m)', style='.', c='b', lw=0,
                                       ax=ax, alpha=0.01, legend=False)

                if hist:
                    subset_pos_charge['alt(m)'].hist(ax=ax2, color='r',
                                                     alpha=0.5,
                                                     orientation='horizontal',
                                                     bins=1000, lw=0)
                    subset_neg_charge['alt(m)'].hist(ax=ax2, color='b',
                                                     alpha=0.5,
                                                     orientation='horizontal',
                                                     bins=1000, lw=0)
                    ax2.set_title('Altitude Histogram')
                    ax2.set_xlabel('Number of sources')

                s = '{0} - {1}'.format(ind_start[:-4], ind_end[:-4])
                t_peaks.append(ind_start)
                pos_peaks.append(self._calculate_histogram(subset_pos_charge))
                neg_peaks.append(self._calculate_histogram(subset_neg_charge))

                ax.set_title('Sources ({0} UTC)'.format(s))
                ax.set_xlabel(r'Time')
                ax.set_ylabel('Altitude (m)')
    
                ax.grid(True)
                ax.set_ylim([0, 16e3])

                if savefigs:
                    file_name = path
                    s = datetime.datetime.strftime(start_time, '%Y%m%d-%H%M%S')
                    file_name += 'storm_%s.png' % s

                    # print(file_name)
                    # plt.show()
                    fig.savefig(file_name, format='png', dpi=300)

            except TypeError as e:
                pass
    
            start_time = end_time
            end_time += t_increment

        # Print and plot summary of pos and neg peaks on each interval
        pos_series = pd.Series(pos_peaks, index=t_peaks)
        neg_series = pd.Series(neg_peaks, index=t_peaks)

        temp = pd.DataFrame({'positive': pos_series, 'negative': neg_series})
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        temp.plot(y='positive', ax=ax, c='r')
        temp.plot(y='negative', ax=ax, c='b')
        ax.set_title('Histogram Peak Altitudes for Each Interval')
        ax.set_ylabel('Altitude (m)')
        ax.set_xlabel('Time')
        plt.show()

    def print_storm_summary(self, charge=None, flash_types=None):
        """ Print the summary of the storm. """

        s = "\nLMA File: Charge {0}".format(charge.upper())
        print(s)
        print('-' * len(s))

        if charge is None:
            storm = self.storm
        elif charge == 'positive':
            storm = self.storm[self.storm['charge'] == 3]
        elif charge == 'negative':
            storm = self.storm[self.storm['charge'] == -3]
        elif charge == 'other':
            storm = self.storm[self.storm['charge'] == 0]

        # Get rid of unwanted columns
        storm.pop('time(UT-sec-of-day)')
        # storm.pop('lat')
        # storm.pop('lon')
        storm.pop('reduced-chi^2')
        storm.pop('#-of-stations-contributed')
        storm.pop('flash-number')
        storm.pop('charge')

        print(storm.describe())
        print('\n')

    def save_to_pickle(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self.__dict__, f)


class StormODS(Storm):
    """
    An object for analyzing data exported from Excel or LibreOffice using the
    Pandas module.

        Parameters:
        -----------
        storm: Pandas DataFrame (optional)
            Contains the entire data set merged from files.

        Attributes:
        -----------
        storm: Pandas DataFrame
            Contains the entire data set..

    """

    def __init__(self, storm=None):
        """ Initialize the object. """
        super(StormODS, self).__init__(storm)

    @staticmethod
    def _parse_ods_file(file):
        """ Parse the .ods files to generate the DataFrame. """

        storm = pd.read_csv(file)

        # Combine the date and time columns into a single datetime column
        storm.insert(0, 'DateTime',
                     ['{0} {1}'.format(storm['Date'][i], storm['Time'][i])
                      for i in
                      range(len(storm))])
        storm['DateTime'] = pd.to_datetime(storm['DateTime'],
                                           format='%m/%d/%y %H:%M:%S.%f')
        storm.set_index('DateTime', inplace=True)

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

    def analyze_flash_areas(self, flash_type='all'):
        """ Analyze the areas of the specified flash type. """

        temp_storm = self.get_flash_type(flash_type=flash_type)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        temp_storm['Area (km^2)'].hist(ax=ax)
        ax.set_title('Histogram of flash areas for '
                     '{0}s'.format(flash_type.upper()))
        ax.set_xlabel('Flash area (km^2)')
        ax.set_ylabel('Number of flashes')

        print(temp_storm['Area (km^2)'].describe())

        plt.show()

    def analyze_initiation_heights(self, flash_type='all'):
        """ Analyze the initiation heights of the specified flash type. """

        temp_storm = self.get_flash_type(flash_type=flash_type)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        temp_storm['Initiation Height (km)'].hist(ax=ax)
        ax.set_title('Histogram of initiation heights for '
                     '{0}s'.format(flash_type.upper()))

        ax.set_xlabel('Initiation Height (km)')
        ax.set_ylabel('Number of flashes')

        print(temp_storm['Initiation Height (km)'].describe())

        plt.show()

    def calculate_flash_rates(self, interval=5, flash_type='all'):
        """
        Calculate and print the flash rates in the specified time interval
        for the specified flash types.

        Parameters
        ----------
        interval: int
            Time interval in minutes.
        flash_type: str
            Flash type to do the calculation.

        Returns
        -------
            temp_storm: DataFrame
                DataFrame containing all the data of all flashes for the
                specified flash type.

        """
        # Calculate flash rate every 5 minutes
        t_interval = datetime.timedelta(minutes=interval)
        t_start = self.storm.index.min()
        t_end = t_start + t_interval

        if flash_type.lower == 'all':
            temp_storm = self.storm
        else:
            temp_storm = self.storm[self.storm['Type'] == flash_type.upper()]

        # if flash_type.lower() == 'ic':
        #     temp_storm = self.storm[self.storm['Type'] == 'IC']
        #
        # elif flash_type.lower() == '-cg' or flash_type.lower() == 'cg':
        #     storm1 = self.storm[self.storm['Type'] == '-CG']
        #     storm2 = self.storm[self.storm['Type'] == 'CG']
        #
        #     temp_storm = pd.concat([storm1, storm2], ignore_index=True)
        # else:
        #     temp_storm = self.storm

        s = '\nFlash rate for {0} flashes (interval = {1} minutes):'.format(
            flash_type.upper(), interval)
        print(s)
        print('-' * len(s))

        rates = []
        while t_start < self.storm.index.max():
            temp = temp_storm[temp_storm.index < t_end]
            temp = temp[temp.index >= t_start]

            start = datetime.datetime.strftime(t_start, '%H:%M:%S.%f')[:-4]
            end = datetime.datetime.strftime(t_end, '%H:%M:%S.%f')[:-4]

            rate = (len(temp) / t_interval.total_seconds()) * 60
            rates.append(rate)

            t_start = t_end
            print('{0} -- {1} UTC = {2:0.2f} '
                  '/min ({3} flashes total)'.format(start, end, rate,
                                                    len(temp)))
            t_end += t_interval

        # Entire self.storm flash rate
        rates = np.array(rates)
        r = self.storm.index.max() - self.storm.index.min()
        rate = len(temp_storm) / r.total_seconds() * 60

        print('\nNumber of {0}s: {1} out of {2} total '
              '({3:0.2f}%)'.format(flash_type.upper(), len(temp_storm),
                                   len(self.storm),
                                   len(temp_storm) / len(self.storm) * 100))

        print('Average {0} rate of entire storm: {1:0.2f} '
              'per minute'.format(flash_type.upper(), rate))

        s = '\nInterval {0} Rate Statistics:'.format(flash_type.upper())
        print(s)
        print('-' * len(s))
        print('Mean: {0:0.2f} per minute'.format(np.mean(rates)))
        print('Std. dev. {0:0.2f} per minute'.format(np.std(rates)))
        print('Max {0:0.2f} per minute'.format(np.max(rates)))
        print('Minimum {0:0.2f} per minute'.format(np.min(rates)))

        return temp_storm

    @classmethod
    def from_ods_file(cls, file):
        """ Initialize the object from files and dates """

        storm = cls._parse_ods_file(file)
        return cls(storm)

    def get_analyzed_flash_numbers(self, storm_lma):
        """
        Get the LMA flash number that corresponds to the analyzed flashes
        in the .ods file.

        Parameters:
        -----------
            storm_lma: Storm object
                Storm object representing the data from a .dat file.

        Returns:
        --------
            data_frame: DataFrame
                DataFrame containing a copy of self.storm plus the
                flash-number column.

        """

        # Limit the storm_ods times to the storm times
        start_ind = storm_lma.storm.index.min()
        end_ind = storm_lma.storm.index.max()

        if start_ind < self.storm.index.min():
            start_ind = self.storm.index.min()

        if end_ind > self.storm.index.max():
            end_ind = self.storm.index.max()

        data_frame = self.storm.loc[start_ind:end_ind]

        # Setup the container for the results data
        analyzed_flashes = dict()
        analyzed_flashes['flash-number'] = []
        analyzed_flashes['DateTime'] = []

        temp = storm_lma.storm[storm_lma.storm['charge'] != 0]
        numbers = temp['flash-number'].unique()

        # Start the computation
        count = 1
        total = len(data_frame.index) * len(numbers)

        print('Total Iterations: {0}'.format(total))
        start = datetime.datetime.now()
        for i in data_frame.index:
            # # Ignore the times in the file that are outside the range of
            # # the analyzed storm.
            # if not (self.storm.index.min() <= i <= self.storm.index.max()):
            #     continue

            number_list = []
            for flash_number in numbers:
                flash = storm_lma.storm[storm_lma.storm['flash-number'] ==
                                        flash_number]
                dt = datetime.timedelta(microseconds=30000)  # 0.03 sec

                if flash.index.min() - dt < i < flash.index.max() + dt:
                    number_list.append(flash_number)

                count += 1
                print('Analyzing... {0:0.2f}%'.format(count / total * 100),
                      end='\r')

            if number_list:
                if len(number_list) == 1:
                    number_list = number_list[0]
                else:
                    number_list = tuple(number_list)

                analyzed_flashes['flash-number'].append(number_list)
                analyzed_flashes['DateTime'].append(i)

        end = datetime.datetime.now()
        print('Analysis time: {0}\n'.format(end - start))

        series = pd.Series(analyzed_flashes['flash-number'],
                           index=analyzed_flashes['DateTime'])

        series.drop_duplicates(keep='first', inplace=True)

        data_frame.loc[:, 'flash-number'] = series

        return data_frame

    def get_flash_type(self, flash_type='all'):
        """ Returns a DataFrame with all the flashes of a certain type. """

        if flash_type.lower == 'all':
            temp_storm = self.storm
        else:
            temp_storm = self.storm[self.storm['Type'] == flash_type.upper()]

        return temp_storm

    def plot_flash_type(self, storm_lma, type='IIC'):
        """
        Plot the LMA sources of each file type as classified in the .ods
        file generated during analysis.

        Parameters
        ----------
        storm_lma: Storm
            Storm object containing the LMA data.
        type: str (optional)
            Flash type

        """

        if type not in self.storm['Type'].unique():
            print('Flash type not found.')
            return False

        flashes = self.storm[self.storm['Type'] == type]
        dt = datetime.timedelta(microseconds=200000)  # 200 ms

        for i in flashes.index:
            t1 = flashes.loc[i]['DateTime'] - dt
            t2 = flashes.loc[i]['DateTime'] + \
                 flashes.loc[i]['Duration(s)'] + dt

            p = storm_lma.get_flash_plotter(t1, t2)
            p.plot_all()
            plt.show()

    def print_storm_summary(self, charge=None, flash_types=None):
        """ Print the summary of the storm. """

        if flash_types is None:
            types = self.storm['Type'].unique()
        else:
            types = flash_types

        for t in types:
            storm = self.storm[self.storm['Type'] == t]
            s = '\n'
            s += '{0} : {1}\n'.format(t, len(storm))

            # Get rid of unwanted columns
            storm.pop('EW Extent (km)')
            storm.pop('NS Extent (km)')

            print(s)
            print(storm.describe())

    def save_to_pickle(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def sort_flashes_into_cells(self, storm_lma, times, xlims,
                                ylims, cell_names):

        """
        Sort the analyzed flashes in the ODS files by cells using the LMA
        sources from the LMA exported file into defined cells. This method
        can only be called on an ODS storm.

            Parameters:
            -----------
                storm_lma: Storm
                    Storm object containing the LMA data
                times: list
                    List of times for which the limits and name of each cell
                    is defined.
                xlims: list
                    List of tuples containing the limits in the x-direction of
                    each cell at each time.
                ylims: list
                    List of tuples containing the limits in the y-direction of
                    each cell at each time.
                cell_names: list
                    List of names for each cell.

        """

        # Make sure the current ODS storm has the LMA flash numbers for each
        # flash
        if 'flash-number' not in self.storm.columns:
            self.storm = storm_lma.get_analyzed_flash_numbers(self.storm)

        # Remove all the entries that are Nan and sort the indices
        storm = self.storm.dropna(subset=['flash-number'])
        storm.sort_index(inplace=True)

        # Convert the times list into datetime
        # This assumes only one date per .ods file
        s = '{0}/{1}/{2}'.format(storm.index[0].month, storm.index[0].day,
                                 storm.index[0].year)
        for i in range(len(times)):
            times[i] = datetime.datetime.strptime(s + ' ' + times[i],
                                                  '%m/%d/%Y %H%M')

        # If xlims or ylims is a constant, duplicate that value so that the
        # length of the lists are the same, using the times list as the base.

        if len(xlims[0]) == 1:
            temp_x1 = xlims[0]
            temp_x2 = xlims[1]
            xlims = []

            for i in range(len(times)):
                xlims.append((temp_x1, temp_x2))

        if len(ylims[0]) == 1:
            temp_y1 = ylims[0]
            temp_y2 = ylims[1]
            ylims = []

            for i in range(len(times)):
                ylims.append((temp_y1, temp_y2))

        # Start loop
        for i in range(len(times) - 1):
            t_start = times[i]
            t_end = times[i+1]

            if t_start < storm.index.min():
                t_start = storm.index.min()
            if t_end > storm.index.max():
                t_end = storm.index.max()

            temp = storm.loc[t_start:t_end]

            results = dict()
            results['DateTime'] = []
            results['Cell'] = []

            for index, row in temp.iterrows():
                sources = storm_lma.get_sources_from_flash_number(
                                                           row['flash-number'])
                flash = self.StormLMA(sources)
                flash.convert_latlon_to_km(3, 4)

                flash = flash.storm[flash.storm['x (m)'] > xlims[i][0]]
                flash = flash.storm[flash.storm['x (m)'] < xlims[i][1]]
                flash = flash.storm[flash.storm['y (m)'] > ylims[i][0]]
                flash = flash.storm[flash.storm['y (m)'] < ylims[i][1]]

                if len(flash) > 0:
                    results['DateTime'].append(index)
                    results['Cell'].append(cell_names[i])

                else:
                    results['DateTime'].append(index)
                    results['Cell'].append(None)
