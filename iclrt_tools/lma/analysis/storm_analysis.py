#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import dates
import datetime
import numpy as np
import pickle
import seaborn as sns
import os
import numpy as np
import scipy
import scipy.signal
import sys
import tqdm

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

    def convert_latlon_to_m(self, x_col=None, y_col=None, verbose=False):
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
        results['x(m)'] = []
        results['y(m)'] = []

        total = len(self.storm)

        if verbose:
            pbar = tqdm.tqdm(total=total)

        for i, s in self.storm.iterrows():
            if verbose:
                pbar.update(1)

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
            results['x(m)'].append(x)
            results['y(m)'].append(y)

        # Insert the x result into the DataFrame
        x_series = pd.Series(results['x(m)'], index=results['DateTime'])

        if x_col is None:
            x_col = len(self.storm.columns)

        self.storm.insert(x_col, 'x(m)', x_series)

        # Insert the y result into the DataFrame
        y_series = pd.Series(results['y(m)'], index=results['DateTime'])

        if y_col is None:
            y_col = len(self.storm.columns)

        self.storm.insert(y_col, 'y(m)', y_series)

    def get_column_series(self, col):
        if col in self.storm.columns:
            return self.storm[col]
        else:
            raise KeyError(col)

    def __len__(self):
        return len(self.storm)


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
    def _calculate_histogram(data_series, column, **kwargs):
        """ Compute the histogram of a Series and return the bin centers. """

        # Extract data from DataSeries into a np array
        data = np.array(data_series[column].dropna())

        # Calculate histogram of the data and find the bin centers
        hist, bin_edges = np.histogram(data, **kwargs)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Return the altitude (bin_center) of the largest value
        # in the histogram
        return hist, bin_centers, bin_edges

    @staticmethod
    def _calculate_histogram_max(data_series, column):
        """ Compute the histogram of a Series and return the bin centers. """

        # Extract data from DataSeries into a np array
        data = np.array(data_series[column].dropna())

        # Calculate histogram of the data and find the bin centers
        hist, bin_edges = np.histogram(data, bins=1000)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Return the altitude (bin_center) of the largest value
        # in the histogram
        return bin_centers[np.argmax(hist)]

    @staticmethod
    def _parse_lma_files(files, dates):
        """ Parse the LMA .csv files to generate the DataFrame. """

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
        storm.sort_index(inplace=True)
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
                                  'Mult', 'Dummy'])

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

    def copy(self):
        return StormLMA(self.storm.copy())

    def filtered_stations(self, num_stations=6, inplace=True):
        # Filter data by number of stations.
        # The default filtereding is 6 or more stations.

        storm = self.storm
        storm = storm[storm['#-of-stations-contributed'] >= num_stations]

        if inplace:
            self.storm = storm
        else:
            return storm

    def filtered_chi_squared(self, chi_sq=5, inplace=True):
        # Filter data by chi^2 value.
        # The default filtereding is a chi^2 <= 5.

        storm = self.storm
        storm = storm[storm['reduced-chi^2'] <= chi_sq]

        if inplace:
            self.storm = storm
        else:
            return storm

    @classmethod
    def from_lma_files(cls, files, dates, num_stations=6, chi_sq=5):
        """ Initialize the object from files and dates """

        storm = cls._parse_lma_files(files, dates)
        storm = cls(storm)
        storm.filtered_stations(num_stations)
        storm.filtered_chi_squared(chi_sq)

        return storm

    def from_pickle(self, file):
        """ Initialize the object from a save pickle. """

        tmp_dict = pickle.load(open(file, 'rb'))

        self.__dict__.update(tmp_dict)

    def get_charge_regions(self):
        """ Return DataFrames corresponding to each charge region. """

        # Generate a DataFrame for all positive charge sources
        self.positive_charge = self.storm[self.storm['charge'] == 3]
    
        # Generate a DataFrame for all negative charge sources
        self.negative_charge = self.storm[self.storm['charge'] == -3]
    
        # Generate a DataFrame for all non-determined sources from the
        # classified flash numbers from above
        numbers = self.negative_charge['flash-number'].unique()
        numbers = np.append(numbers,
                            self.positive_charge['flash-number'].unique())
        numbers = np.unique(numbers)

        self.other = self.storm[self.storm['flash-number'].isin(numbers)]
    
        return self.positive_charge, self.negative_charge, self.other

    def get_lma_from_ods(self, storm_ods):
        """
        Return a StormLMA object with the data corresponding to the flashes
        in the .ods file.

        Parameters
        ----------
        storm_ods: StormODS
            Object containing the flash information to be extracted.

        Returns
        -------
            lma: StormLMA
                StormLMA object containing the data corresponding to the
                flashes in the .ods file

        """

        temp = storm_ods.storm.dropna(subset=['Cell'])
        temp = temp['flash-number'].dropna().unique()

        numbers = []
        for n in temp:
            if type(n) == tuple:
                for m in n:
                    numbers.append(m)
            else:
                numbers.append(n)

        lma = StormLMA(self.get_sources_from_flash_number(numbers))

        return lma

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
                if type(n) is tuple or type(n) is list:
                    for m in n:
                        temp.append(self.storm[self.storm['flash-number'] == m])

                else:
                    temp.append(self.storm[self.storm['flash-number'] == n])

                # temp.append(self.storm[self.storm['flash-number'] == n])

            subset = pd.concat(temp)

        subset.sort_index(inplace=True)

        return subset

    def get_flash_plotter_from_number(self, flash_number=None):
        """
        Get the LMA sources for flash_number.

        Parameters
        ----------
            flash_number: int, float, or list (optional)
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
                if type(n) is tuple or type(n) is list:
                    for m in n:
                        temp.append(self.storm[self.storm['flash-number'] == m])

                else:
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
                     'NA',
                     str(subset['P(dBW)'][ind]),
                     'NA',
                     str(subset['charge'][ind]),
                     str(subset['mask'][ind])])

                data += '\n'

                f.write(data)

        # sys.exit(1)
        # Create the LMAPlotter object and run the measure_area() function
        p = df.LMAPlotter(temp_file, charge=True)

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

    def get_initial_plotter_from_number(self, flash_number=None,
                                        number_of_sources=20):
        """
        Get the initial 20 LMA sources for flash_number.

        Parameters
        ----------
            flash_number: int, float, or list (optional)
                Flash number to get.
            number_of_sources: int
                Number of sources to get from the beginning of the flash.

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
            subset.sort_index(inplace=True)
            subset = subset.iloc[0:number_of_sources]

        else:
            temp = []
            for n in flash_number:
                if type(n) is tuple or type(n) is list:
                    for m in n:
                        f = self.storm[self.storm['flash-number'] == m]
                        f.sort_index(inplace=True)
                        f = f.iloc[0:number_of_sources]
                else:
                    f = self.storm[self.storm['flash-number'] == n]
                    f.sort_index(inplace=True)
                    f = f.iloc[0:number_of_sources]

                temp.append(f)

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

    def get_flash_number_count(self):
        """ Return the count for all flash numbers in the file. """

        grouped = self.storm.groupby(['flash-number'])
        flash_number_count = grouped.size().reset_index()
        flash_number_count.columns = ['flash-number', 'count']

        return flash_number_count

    def get_flashes_by_size(self, size='big'):
        """
        Return a DataFrame with the sources corresponding to the flash
        size as defined by the xlma sorting algorithm.

        The choices are:
            'big' : 75 or more sources
            'medium': 11 - 74 sources

        Parameters
        ----------
        size: str
            String corresponding to the desired flash size.

        Returns
        -------
        df: DataFrame
            DataFrame with the sources that correspond to flashes of the
            specified size.

        """

        # Count the number of sources for each flash-number
        flash_number_count = self.get_flash_number_count()

        # Sort the flash numbers according to the specified size
        if size == 'big':
            flash_numbers = flash_number_count[flash_number_count['count'] >=
                                               75]
        else:  # elif size == 'medium':
            flash_numbers = flash_number_count[flash_number_count['count'] >=
                                               11]
            flash_numbers = flash_numbers[flash_numbers['count'] < 75]

        # Get all sources for the specified size
        pds = []
        for fn in flash_numbers['flash-number']:
            pds.append(self.storm[self.storm['flash-number'] == fn])

        flashes = pd.concat(pds, ignore_index=True)

        # Return final DataFrame
        return flashes

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
                           show_plot=False, include_all=False):
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

        if include_all:
            positive_charge, negative_charge, other = self.get_charge_regions()
        else:
            positive_charge, negative_charge, _ = self.get_charge_regions()
    
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

        if include_all:
            other.plot(y='alt(m)', style='.', c='g', lw=0, alpha=0.01,
                       ax=ax, legend=False)

        charge.plot(y='alt(m)', style='.', c=color, lw=0, alpha=0.01,
                    ax=ax, legend=False)
    
        if hist:
            charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                  color=color, alpha=0.5, bins=1000, lw=0)
    
            ax2.set_title('Altitude Histogram')
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
    
    def plot_all_charge_regions(self, hist=True, show_plot=False,
                                include_all=False, alpha=0.01):
        """
        Plot both charge regions together. The source histograms can also
        be plotted. The default is to not show the plot.

        Parameters
        ----------
            hist: bool (optional)
                Boolean flag to show the histogram in the plot
            show_plot: bool (optional)
                Boolean flag to show the plot
            include_all: bool (optional)
                Boolean flag to include unclassified sources.

        Returns
        -------
            fig: matplotlib.Figure
                Figure instance of plot
            ax: matplotlib.Axes
                Axis instance of plot
            ax2: matplotlib.Axes
                Axis instance of histogram (only when hist is True)

        """

        if include_all:
            positive_charge, negative_charge, other = self.get_charge_regions()
        else:
            positive_charge, negative_charge, _ = self.get_charge_regions()
    
        # Plot both charge sources and histogram
        if hist:
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
        else:
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        if include_all:
            other.plot(y='alt(m)', style='.', c='g', lw=0,
                       alpha=alpha, ax=ax, legend=False)

        if not positive_charge.empty:
            positive_charge.plot(y='alt(m)', style='.', c='r', lw=0,
                                 alpha=alpha, ax=ax, legend=False)
        if not negative_charge.empty:
            negative_charge.plot(y='alt(m)', style='.', c='b', lw=0,
                                 alpha=alpha, ax=ax, legend=False)
    
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
            ax2.set_title('Altitude Histogram')
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

    def plot_interval_sources(self, interval=5, hist=True,
                              savefigs=False, path='./', include_all=True):

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

        if include_all:
            positive_charge, negative_charge, other = self.get_charge_regions()
        else:
            positive_charge, negative_charge, _ = self.get_charge_regions()
    
        start_time = positive_charge.index.min()
        end_time = start_time + t_increment

        while start_time < positive_charge.index.max():
            ind_start = datetime.datetime.strftime(start_time,
                                                   '%Y-%m-%d %H:%M:%S.%f')
            ind_end = datetime.datetime.strftime(end_time,
                                                 '%Y-%m-%d %H:%M:%S.%f')

            # subset = self.storm.loc[start_time:end_time]  #[ind_start, ind_end]
            # subset_pos_charge = subset[subset['charge'] == 3]
            # subset_neg_charge = subset[subset['charge'] == -3]
            # subset_other = subset[subset['charge'] == 0]

            subset_pos_charge = positive_charge.loc[start_time:end_time]
            subset_neg_charge = negative_charge.loc[start_time:end_time]

            if include_all:
                subset_other = other[start_time:end_time]

            try:

                if hist:
                    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6),
                                                  sharey=True)
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

                if include_all:
                    subset_other.plot(y='alt(m)', style='.', c='g', lw=0,
                                      alpha=0.01, ax=ax, legend=False)

                subset_pos_charge.plot(y='alt(m)', style='.', c='r', lw=0,
                                       alpha=0.01, ax=ax, legend=False)
                subset_neg_charge.plot(y='alt(m)', style='.', c='b', lw=0,
                                       ax=ax, alpha=0.01, legend=False)

                if hist:
                    pos_alt = subset_pos_charge['alt(m)']
                    pos_alt.hist(ax=ax2, color='r',
                                 alpha=0.5,
                                 orientation='horizontal',
                                 bins=1000, lw=0)

                    neg_alt = subset_neg_charge['alt(m)']
                    neg_alt.hist(ax=ax2, color='b',
                                 alpha=0.5,
                                 orientation='horizontal',
                                 bins=1000, lw=0)
                    ax2.set_title('Altitude Histogram')
                    ax2.set_xlabel('Number of sources')

                s = '{0} - {1}'.format(ind_start[:-4], ind_end[:-4])
                ax.set_title('Sources ({0} UTC)'.format(s))
                ax.set_xlabel(r'Time')
                ax.set_ylabel('Altitude (m)')

                ax.grid(True)
                ax.set_ylim([0, 16e3])

                if savefigs:
                    file_name = path
                    s = datetime.datetime.strftime(start_time,
                                                   '%Y%m%d-%H%M%S')
                    file_name += 'storm_%s.png' % s

                    # print(file_name)
                    # plt.show()
                    fig.savefig(file_name, format='png', dpi=300)

            except TypeError as e:
                pass
    
            start_time = end_time
            end_time += t_increment

        return fig, ax

    def plot_interval_trends(self, interval=5, ax=None,
                             savefig=False, path='./', ):

        """
        Generate a plot of the trends of the charge regions, more specifically,
        the altitudes of most sources in each time period, starting
        at the time of the earliest positive source and every 'interval'
        minutes. The plot can be saved if the user wants.

            Parameters:
            -----------
            interval: int (optional)
                Time interval in minutes.
            ax: mpl Axes (optional)
                Matplotlib Axes instance to place the plot.
            savefig: bool (optional)
                Boolean flag to save the plot.
            path: str (optional)
                Path onto which the plot will be saved.

            Returns:
            --------
            fig: mpl Figure
                Figure instance.
            ax: mpl Axes
                Axes instance

        """

        # Plot both charge regions and histogram at a certain
        # interval (in minutes).
        t_increment = datetime.timedelta(seconds=interval * 60)

        positive_charge, negative_charge, _ = self.get_charge_regions()

        start_time = positive_charge.index.min()
        if negative_charge.index.min() < start_time:
            start_time = negative_charge.index.min()

        end_time = start_time + t_increment

        # These lists will hold the altitude of the peak of each histogram as
        # well as the time interval when they occur
        t_peaks = []
        pos_peaks = []
        neg_peaks = []

        max_time = positive_charge.index.max()

        if negative_charge.index.max() > max_time:
            max_time = negative_charge.index.max()

        while start_time < max_time:
            ind_start = datetime.datetime.strftime(start_time,
                                                   '%Y-%m-%d %H:%M:%S.%f')
            ind_end = datetime.datetime.strftime(end_time,
                                                 '%Y-%m-%d %H:%M:%S.%f')

            subset = self.storm.loc[start_time:end_time]
            subset_pos_charge = subset[subset['charge'] == 3]
            subset_neg_charge = subset[subset['charge'] == -3]

            if not subset.empty:
                t_peaks.append(ind_start)
                temp = self._calculate_histogram_max(subset_pos_charge,
                                                     'alt(m)')
                pos_peaks.append(temp)

                temp = self._calculate_histogram_max(subset_neg_charge,
                                                     'alt(m)')
                neg_peaks.append(temp)

            start_time = end_time
            end_time += t_increment

        # Print and plot summary of pos and neg peaks on each interval
        pos_series = pd.Series(pos_peaks, index=t_peaks)
        neg_series = pd.Series(neg_peaks, index=t_peaks)

        temp = pd.DataFrame({'positive': pos_series, 'negative': neg_series})

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        else:
            fig = ax.get_figure()

        temp.plot(y='positive', ax=ax, c='r')
        temp.plot(y='negative', ax=ax, c='b')

        ax.set_title('Histogram Peak Altitudes for Each Interval')
        ax.set_ylabel('Altitude (m)')
        ax.set_xlabel('Time')

        return fig, ax

    def plot_power_histogram(self, ax=None, sep_charges=False, **histargs):
        """
        Plot the power histogram. The user can specify to plot
        a separate histogram for each charge polarity.

        Parameters
        ----------
        ax: mpl Axes object, optional
            Axes object to plot.
        sep_charges: bool, optional
            Flag to plot separate histograms for each charge.
        histargs : object
            Arguments for the computation of the histogram.

        Returns
        -------
        ax: mpl Axes
            mpl Axes of figure

        """

        if ax is not None:
            fig = ax.get_figure()
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        if sep_charges:
            # Calculate histogram
            hist_dict = self.power_histogram(sep_charges=sep_charges,
                                             **histargs)

            # Extract data to plot
            pos_bin = hist_dict['positive']['bins']
            pos_hist = hist_dict['positive']['hist']

            neg_bin = hist_dict['negative']['bins']
            neg_hist = hist_dict['negative']['hist']

            other_bin = hist_dict['other']['bins']
            other_hist = hist_dict['other']['hist']

            # Plot data
            ax.plot(pos_bin, pos_hist, '-r', alpha=0.5)
            ax.plot(neg_bin, neg_hist, '-b', alpha=0.5)
            ax.plot(other_bin, other_hist, '-g', alpha=0.5)

        else:
            # Calculate histogram
            hist_dict = self.power_histogram(sep_charges=sep_charges,
                                             **histargs)

            # Extract data to plot
            bins = hist_dict['all']['bins']
            hist = hist_dict['all']['hist']

            mu = self.storm['P(dBW)'].mean()
            sigma = self.storm['P(dBW)'].std()
            gaussian = mpl.mlab.normpdf(bins, mu, sigma)
            gaussian *= max(hist)

            ax.plot(bins, hist, '-g', alpha=0.5)
            ax.plot(bins, gaussian, '-k')

        ax.set_xlabel('Power (dBW)')
        ax.set_ylabel('Count')

        return ax

    def power_histogram(self, sep_charges=False, **histargs):
        hist_dict = dict()

        if sep_charges:
            # Get different charge regions
            pos, neg, other = self.get_charge_regions()

            # Calculate histogram
            pos_hist, pos_bin, _ = self._calculate_histogram(pos, 'P(dBW)',
                                                             **histargs)
            neg_hist, neg_bin, _ = self._calculate_histogram(neg, 'P(dBW)',
                                                             **histargs)
            other_hist, other_bin, _ = self._calculate_histogram(other,
                                                                 'P(dBW)',
                                                                 **histargs)

            # Remove bins with zero events
            indices = np.where(pos_hist == 0, [False], [True])
            pos_hist = pos_hist[indices]
            pos_bin = pos_bin[indices]

            indices = np.where(neg_hist == 0, [False], [True])
            neg_hist = neg_hist[indices]
            neg_bin = neg_bin[indices]

            indices = np.where(other_hist == 0, [False], [True])
            other_hist = other_hist[indices]
            other_bin = other_bin[indices]

            hist_dict['positive'] = {'hist': pos_hist, 'bins': pos_bin}
            hist_dict['negative'] = {'hist': neg_hist, 'bins': neg_bin}
            hist_dict['other'] = {'hist': other_hist, 'bins': other_bin}

        else:
            hist, bins, _ = self._calculate_histogram(self.storm, 'P(dBW)',
                                                      **histargs)
            indices = np.where(hist == 0, [False], [True])
            hist = hist[indices]
            bins = bins[indices]

            hist_dict['all'] = {'hist': hist, 'bins': bins}

        return hist_dict

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

    def save_flashes_by_size(self, size, file_name):
        """ Save the DataFrame to both CSV and Pickle. """

        data_frame = self.get_flashes_by_size(size)
        data_frame.to_pickle(file_name)
        data_frame.to_csv(file_name, index=False)

    def save_flash_number_count(self, file_name):
        """ Save the flash number count DataFrame to both CSV and Pickle. """
        data_frame = self.get_flash_number_count()
        data_frame.to_pickle(file_name)
        data_frame.to_csv(file_name, index=False)

    def save_to_csv(self, file_name):
        """ Save entire StormLMA object to a CSV. """
        self.storm.to_csv(file_name, index=False)

    def save_to_pickle(self, file_name):
        """ Save entire StormLMA object to a pickle. """
        with open(file_name, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def sort_flashes_into_cells(self, times, xlims, ylims, cell_names,
                                inplace=True):

        """
        Sort the LMA sources from the LMA exported file into defined cells.

            Parameters:
            -----------
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
                inplace: bool (optional)
                    Boolean to apply the results to the current object

        """
        # Convert all coordinates to m if not done so already
        if not ('x(m)' in self.storm.columns):
            print("Converting coordinates to meters...")
            self.convert_latlon_to_m(verbose=True)

        # Remove all the entries that are Nan and sort the indices
        storm = self.storm.dropna(subset=['flash-number'])
        storm.sort_index(inplace=True)

        # If xlims, ylims, or cell_names is a constant, duplicate that value
        # so that the length of the lists are the same, using the times list
        # as the base.

        if not isinstance(xlims[0], np.ndarray):
            if type(xlims[0]) != tuple:
                if type(xlims[0]) != list:
                    temp_x1 = xlims[0]
                    temp_x2 = xlims[1]
                    xlims = []

                    for i in range(len(times)):
                        xlims.append((temp_x1, temp_x2))

        if not isinstance(xlims[0], np.ndarray):
            if type(ylims[0]) != tuple:
                if type(ylims[0]) != list:
                    temp_y1 = ylims[0]
                    temp_y2 = ylims[1]
                    ylims = []

                    for i in range(len(times)):
                        ylims.append((temp_y1, temp_y2))

        if type(cell_names[0]) == str:
            temp_name = cell_names[0]
            cell_names = []

            for i in range(len(times)):
                cell_names.append(temp_name)

        # Start loop
        results = dict()
        results['DateTime'] = []
        results['Cell'] = []
        flash_count = 0

        for i in range(len(times) - 1):
            print('Processing: {0} -- {1} UTC.'.format(times[i], times[i+1]))
            t_start = times[i]
            t_end = times[i+1]

            if t_start < storm.index.min():
                t_start = storm.index.min()
            if t_end > storm.index.max():
                t_end = storm.index.max()

            temp = storm.loc[t_start:t_end]

            for index, row in temp.iterrows():
                # print(row)
                # print(xlims[i])
                if xlims[i][0] < row['x(m)'] < xlims[i][1]:
                    if ylims[i][0] < row['y(m)'] < ylims[i][1]:
                        flash_count += 1
                        results['DateTime'].append(index)
                        results['Cell'].append(cell_names[i])

                # else:
                #     results['DateTime'].append(index)
                #     results['Cell'].append(pd.np.nan)

            print('  Flashes found: {0}'.format(flash_count))

        print('\nDone!')
        results = pd.Series(results['Cell'], index=results['DateTime'],
                            name='Cell')

        # Remove duplicate indices
        results = results.reset_index()
        results.sort_values(by='Cell', inplace=True)
        results.drop_duplicates(subset='index', inplace=True)
        results.set_index('index', inplace=True)
        results.sort_index(inplace=True)

        if inplace:
            self.storm.loc[:, 'Cell'] = results
        else:
            temp = self.storm.copy()
            temp.loc[:, 'Cell'] = results
            return temp

    def sort_flashes_into_cells2(self, cells,
                                 inplace=True):

        """
        Sort the LMA sources from the LMA exported file into defined cells.

            Parameters:
            -----------
                cells: list
                    List of Cell objects to sort
                inplace: bool (optional)
                    Boolean to apply the results to the current object

        """
        # Convert all coordinates to m if not done so already
        if not ('x(m)' in self.storm.columns):
            print("Converting coordinates to meters...")
            self.convert_latlon_to_m(verbose=True)

        # Remove all the entries that are Nan and sort the indices
        storm = self.storm.dropna(subset=['flash-number'])
        storm.sort_index(inplace=True)

        print("Total number of sources before cell sorting: ",
              len(storm.index))
        print("Total number of flashes before cell sorting: ",
              len(storm['flash-number'].unique()))

        results = dict()
        results['DateTime'] = []
        results['Cell'] = []

        for cell in cells:
            xlims = cell.xlims
            ylims = cell.ylims
            times = cell.times
            cell_names = cell.name

            print("*" * 50)
            print("Cell {0}:".format(cell_names))
            print("*" * 50)

            # If xlims, ylims, or cell_names is a constant, duplicate that value
            # so that the length of the lists are the same, using the times list
            # as the base.

            if not isinstance(xlims[0], np.ndarray):
                if type(xlims[0]) != tuple:
                    if type(xlims[0]) != list:
                        temp_x1 = xlims[0]
                        temp_x2 = xlims[1]
                        xlims = []

                        for i in range(len(times)):
                            xlims.append((temp_x1, temp_x2))

            if not isinstance(xlims[0], np.ndarray):
                if type(ylims[0]) != tuple:
                    if type(ylims[0]) != list:
                        temp_y1 = ylims[0]
                        temp_y2 = ylims[1]
                        ylims = []

                        for i in range(len(times)):
                            ylims.append((temp_y1, temp_y2))

            if type(cell_names[0]) == str:
                temp_name = cell_names[0]
                cell_names = []

                for i in range(len(times)):
                    cell_names.append(temp_name)

            # Start loop
            flash_count = 0

            for i in range(len(times)):
                print('Processing: {0} -- {1} UTC.'.format(times[i][0],
                                                           times[i][1]))
                t_start = times[i][0]
                t_end = times[i][1]

                if t_start < storm.index.min():
                    t_start = storm.index.min()
                if t_end > storm.index.max():
                    t_end = storm.index.max()

                temp = storm.loc[t_start:t_end]

                for index, row in temp.iterrows():
                    # print(row)
                    # print(xlims[i])
                    if xlims[i][0] < row['x(m)'] < xlims[i][1]:
                        if ylims[i][0] < row['y(m)'] < ylims[i][1]:
                            flash_count += 1
                            results['DateTime'].append(index)
                            results['Cell'].append(cell_names[i])

                    # else:
                    #     results['DateTime'].append(index)
                    #     results['Cell'].append(pd.np.nan)

                print('  Sources found: {0}'.format(flash_count))

        print('\nDone!')
        results = pd.Series(results['Cell'], index=results['DateTime'],
                            name='Cell')

        # Remove duplicate indices
        results = results.reset_index()
        results.sort_values(by='Cell', inplace=True)
        results.drop_duplicates(subset='index', inplace=True)
        results.set_index('index', inplace=True)
        results.sort_index(inplace=True)

        if inplace:
            self.storm.loc[:, 'Cell'] = results

            print("Total number of assigned sources:",
                  len(self.storm.dropna(subset=['Cell']).index))
            print("Total number of assigned flashes:",
                  len(self.storm.dropna(subset=['Cell'])['flash-number'].unique()))
        else:
            temp = self.storm.copy()
            temp.loc[:, 'Cell'] = results

            print("Total number of assigned sources:",
                  len(temp.dropna(subset=['Cell']).index))
            print("Total number of assigned flashes:",
                  len(temp.dropna(subset=['Cell'])['flash-number'].unique()))

            return temp


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

        # Remove unnecessary columns
        # _ = storm.pop('Date')
        # _ = storm.pop('Time')
        # _ = storm.pop('Comments')
        # _ = storm.pop('Duration (ms)')
        try:
            _ = storm.pop('Flash')
        except KeyError:
            pass

        storm['Initiation Height (km)'] = pd.to_numeric(
            storm['Initiation Height (km)'], errors='coerce')

        storm.sort_index(inplace=True)

        return storm

    def analyze_flash_areas(self, flash_type='all', show_plot=True,
                            hist_lims=None):
        """ Analyze the areas of the specified flash type. """

        temp_storm = self.get_flash_type(flash_type=flash_type)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        temp_storm['Area (km^2)'].hist(ax=ax, range=hist_lims)
        ax.set_title('Histogram of Flash Areas (from Plan View) for '
                     '{0}s'.format(flash_type.upper()))
        ax.set_xlabel('Flash area (km^2)')
        ax.set_ylabel('Number of flashes')

        if show_plot:
            plt.show()

        s = '\nType: {0}'.format(flash_type)
        print(s)
        print('-' * len(s))
        print(temp_storm['Area (km^2)'].describe())

        return ax

    def analyze_initiation_heights(self, flash_type='all', show_plot=True,
                                   hist_lims=None):
        """ Analyze the initiation heights of the specified flash type. """

        temp_storm = self.get_flash_type(flash_type=flash_type)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        temp_storm['Initiation Height (km)'].hist(ax=ax, range=hist_lims)
        ax.set_title('Histogram of initiation heights for '
                     '{0}s'.format(flash_type.upper()))

        ax.set_xlabel('Initiation Height (km)')
        ax.set_ylabel('Number of flashes')

        if show_plot:
            plt.show()

        s = '\nType: {0}'.format(flash_type)
        print(s)
        print('-' * len(s))
        print(temp_storm['Initiation Height (km)'].describe())

        return ax

    def calculate_flash_rates(self, interval=5, flash_type='all',
                              plot=False, show_plot=False):
        """
        Calculate and print the flash rates in the specified time interval
        for the specified flash types.

        Parameters
        ----------
        interval: int (optional)
            Time interval in minutes.
        flash_type: str (optional)
            Flash type to do the calculation.
        plot: bool (optional)
            Plot and return the figure axis
        show_plot: bool (optional)
            Show the plot

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
        times = []
        while t_start < self.storm.index.max():
            temp = temp_storm[temp_storm.index < t_end]
            temp = temp[temp.index >= t_start]

            start = datetime.datetime.strftime(t_start, '%H:%M:%S.%f')[:-4]
            end = datetime.datetime.strftime(t_end, '%H:%M:%S.%f')[:-4]

            rate = (len(temp) / t_interval.total_seconds()) * 60
            rates.append(rate)
            times.append(t_start)

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

        if plot or show_plot:
            rs = pd.Series(rates, name='{0} Flash rate'.format(flash_type.upper()),
                           index=pd.to_datetime(times))

            # Convert interval in minutes to fraction of day. There are
            # 86400.0 seconds in a day
            interval = t_interval.total_seconds() / 86400.0

            # ax = rs.plot()
            fig, ax = plt.subplots(1, 1)
            ax.bar(rs.index.to_pydatetime(), rs, width=interval)
            ax.xaxis_date()
            ax.set_title('{0} Flash rate'.format(flash_type.upper()))
            ax.set_ylabel(r'Rate (min$^{-1}$)')
            ax.set_xlabel('Time (UTC)')

        if show_plot:
            plt.show()

        if plot:
            return temp_storm, ax
        else:
            return temp_storm

    def calculate_nldn_efficiency(self, nldn_file, verbose=False):
        """
        Calculate the efficiency of NLDN by correlating the NLDN detected
        flashes with the ODS detected flashes. Save the result as a
        class attribute self.nldn_detections.

        Parameters:
        -----------
        nldn_file: str
            File path to the NLDN file.

        """

        # Read in file
        nldn = pd.read_csv(nldn_file, sep=' ',
                           names=['Date', 'Time', 'lat', 'lon', 'kA', 'Type',
                                  'Mult', 'Dummy'])

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

        # Limit the NLDN times to the storm times
        start_ind = self.storm.index.min() - datetime.timedelta(microseconds=5E5)  # -0.5 sec
        end_ind = self.storm.index.max() + datetime.timedelta(microseconds=5E5)  # + 0.5 sec
        self.nldn = nldn.loc[start_ind:end_ind]
        self.nldn.sort_index(inplace=True)

        # Setup the container for the results data
        nldn_detections = dict()
        nldn_detections['DateTime'] = []
        nldn_detections['ODS_time'] = []
        nldn_detections['ODS_type'] = []

        # Setup counters for number of flashes processed (count), number of
        # flashes with no correlation (empty), and number of flashes with
        # multiple flash numbers (multiple)
        count = 0
        multiple = 0
        empty = 0

        if verbose:
            total = len(self.storm.index)
            print('Total Iterations: {0}'.format(total))
            pbar = tqdm.tqdm(total=total)

        dt = datetime.timedelta(microseconds=1E5)  # 0.1 seconds
        for i in self.storm.index:
            t1 = i - dt
            t2 = i + dt

            nldn_events = self.nldn.loc[t1:t2].index.unique()

            if verbose:
                pbar.update(1)

            if nldn_events is not None:
                if len(nldn_events) == 1:
                    nldn_events = nldn_events[0]
                    nldn_detections['ODS_time'].append(i)
                    nldn_detections['ODS_type'].append(self.storm.loc[i]['Type'])
                    nldn_detections['DateTime'].append(nldn_events)
                    count += 1
                elif len(nldn_events) > 1:
                    multiple += 1
                    for e in nldn_events:
                        count += 1
                        nldn_detections['ODS_time'].append(i)
                        nldn_detections['ODS_type'].append(self.storm.loc[i]['Type'])
                        nldn_detections['DateTime'].append(e)
                else:
                    empty += 1
                    nldn_detections['ODS_time'].append(i)
                    nldn_detections['ODS_type'].append(self.storm.loc[i]['Type'])
                    nldn_detections['DateTime'].append(nldn_events)

        if verbose:
            pbar.close()
            print("Summary: ")
            print("  Total Detections: {0}\n  Empty: {1}\n"
                  "  Multiple: {2}\n  Total Entries: {3}\n"
                  "  Efficiency: {4:0.2f}".format(count, empty, multiple, total, count/total))

        # Make a Series from the ODS times with the time as the index
        series = pd.Series(nldn_detections['ODS_time'],
                           index=nldn_detections['DateTime'])

        # Remove the duplicate indices (if any)
        series = series.reset_index(inplace=False)
        series.drop_duplicates('index', keep='first', inplace=True)
        series.set_index('index', inplace=True)
        series.index.rename('DateTime', inplace=True)
        series.columns = ['ODS_time']

        # Insert series into data_frame
        self.nldn.loc[:, 'ODS_time'] = series

        # Make a Series from the ODS types with the time as the index
        series = pd.Series(nldn_detections['ODS_type'],
                           index=nldn_detections['DateTime'])

        # Remove the duplicate indices (if any)
        series = series.reset_index(inplace=False)
        series.drop_duplicates('index', keep='first', inplace=True)
        series.set_index('index', inplace=True)
        series.index.rename('DateTime', inplace=True)
        series.columns = ['ODS_type']

        # Insert series into data_frame
        self.nldn.loc[:, 'ODS_type'] = series

    @classmethod
    def from_ods_file(cls, file):
        """ Initialize the object from files and dates """

        storm = cls._parse_ods_file(file)
        return cls(storm)

    def from_pickle(self, file):
        """ Initialize the object from a save pickle. """

        tmp_dict = pickle.load(open(file, 'rb'))

        self.__dict__.update(tmp_dict)

    def get_analyzed_flash_numbers(self, storm_lma, verbose=False,
                                   return_duplicates=False):
        """
        Get the LMA flash number that corresponds to the analyzed flashes
        in the .ods file.

        Parameters:
        -----------
            storm_lma: Storm object
                Storm object representing the data from a .dat file.
            verbose: bool (optional)
                Print status.
            return_duplicates: bool (optional)
                Returns the list of duplicate flash numbers in addition to the
                results DataFrame.

        Returns:
        --------
            data_frame: DataFrame
                DataFrame containing a copy of self.storm plus the
                flash-number column.

        """
        # Define the time delta around the ODS timestamps
        dt = datetime.timedelta(microseconds=2e4)  # 20 msec

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

        # Setup counters for number of flashes processed (count), number of
        # flashes with no correlation (empty), and number of flashes with
        # multiple flash numbers (multiple)
        count = 0
        empty = 0
        multiple = 0
        duplicate = 0
        duplicate_list = []

        if verbose:
            total = len(data_frame.index)
            print('Total Iterations: {0}'.format(total))
            pbar = tqdm.tqdm(total=total)

        for i in data_frame.index:
            t1 = i - dt
            t2 = i + dt

            number_list = storm_lma.storm.loc[t1:t2]['flash-number'].unique()

            if verbose:
                pbar.update(1)

            if number_list is not None:
                if len(number_list) == 1:
                    number_list = number_list[0]
                    if number_list in analyzed_flashes['flash-number']:
                        duplicate_list.append(number_list)
                        number_list = np.nan
                        duplicate += 1
                    else:
                        count += 1
                elif len(number_list) > 1:
                    # Remove already matches flashes
                    new_list = []
                    for n in number_list:
                        if n not in analyzed_flashes['flash-number']:
                            new_list.append(n)

                    if len(new_list) == 1:
                        number_list = new_list[0]
                        if number_list in analyzed_flashes['flash-number']:
                            duplicate_list.append(number_list)
                            number_list = np.nan
                            duplicate += 1
                        else:
                            count += 1
                    elif len(new_list) > 1:
                        multiple += 1
                        number_list = tuple(new_list)

                        ### Comment out if you plan on not ignoring these!!!
                        number_list = np.nan
                        ###
                    else:
                        empty += 1
                        number_list = np.nan

                else:
                    empty += 1
                    number_list = np.nan

                analyzed_flashes['flash-number'].append(number_list)
                analyzed_flashes['DateTime'].append(i)

        if verbose:
            pbar.close()
            print("Summary: ")
            print("  Total: {0}\n  Matched: {1}\n  Empty: {2}\n"
                  "  Multiple: {3}\n  Duplicate: {4}".format(total, count,
                                                             empty, multiple,
                                                             duplicate))

        # Make a Series from the duplicated flashes and save as CSV
        duplicate_series = pd.Series(duplicate_list, name='duplicates')

        # Make a Series from the flash-numbers with the time as the index
        series = pd.Series(analyzed_flashes['flash-number'],
                           index=analyzed_flashes['DateTime'],
                           name='flash-number')

        # Remove duplicate flash numbers
        # series.drop_duplicates(keep='first', inplace=True)

        # Remove the duplicate indices (if any)
        series = series.reset_index(inplace=False)
        series.drop_duplicates('index', keep='first', inplace=True)
        # Drop all duplicated single flash-numbers
        series.drop_duplicates('flash-number', keep=False, inplace=True)
        series.set_index('index', inplace=True)
        series.index.rename('DateTime', inplace=True)
        series.columns = ['flash-number']

        # return series

        # Insert series into data_frame
        data_frame.loc[:, 'flash-number'] = series

        if return_duplicates:
            return data_frame, duplicate_series
        else:
            return data_frame

    def get_cell_ods(self, cell_name):
        """
        Return a StormODS object with the data corresponding to cell_name.

            Parameters:
            -----------
                cell_name: str
                    Name of the cell from which to get the data.

            Returns:
            --------
                temp: StormODS
                    StormODS object with the data of cell_name.

        """

        temp = self.storm.groupby('Cell').get_group(cell_name)
        return StormODS(temp)

    def get_entry_from_flash_number(self, number):
        """ Return the row with the information for the flash number. """

        if isinstance(number, list) or isinstance(number, tuple):
            return None

        else:
            return self.storm[self.storm['flash-number'] == int(number)]

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

    def plot_rtl_lines(self, ax, show_plot=False):
        """
        Plot vertical lines corresponding to the times of RTLs.

        Parameters
        ----------
        ax: mpl Axes
            Axes instance to plot lines.

        Returns
        -------
        ax: mpl Axes
            Axes instance

        """
        rtls = self.get_flash_type(flash_type='RTL')
        ymin, ymax = ax.get_ylim()
        ax.vlines(x=rtls.index, ymin=ymin, ymax=ymax, color='r', alpha=0.5,
                  label='RTL Times')
        legend = ax.legend(frameon=True)
        frame = legend.get_frame()
        frame.set_facecolor('#FFFFFF')
        frame.set_edgecolor('#000000')

        if show_plot:
            plt.show()

        return ax

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
                                ylims, cell_names, min_sources=5,
                                inplace=True):

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
                min_sources: int (optional)
                    Minimum number of sources that would be considered a match
                inplace: bool (optional)
                    Boolean to apply the results to the current object

        """

        # Make sure the current ODS storm has the LMA flash numbers for each
        # flash
        if 'flash-number' not in self.storm.columns:
            print('Getting analyzed flash numbers:')
            self.storm = self.get_analyzed_flash_numbers(storm_lma,
                                                         verbose=True)

        # Remove all the entries that are Nan and sort the indices
        storm = self.storm.dropna(subset=['flash-number'])
        storm.sort_index(inplace=True)

        # If xlims, ylims, or cell_names is a constant, duplicate that value
        # so that the length of the lists are the same, using the times list
        # as the base.

        if type(xlims[0]) != tuple:
            if type(xlims[0]) != list:
                temp_x1 = xlims[0]
                temp_x2 = xlims[1]
                xlims = []

                for i in range(len(times)):
                    xlims.append((temp_x1, temp_x2))

        if type(ylims[0]) != tuple:
            if type(ylims[0]) != list:
                temp_y1 = ylims[0]
                temp_y2 = ylims[1]
                ylims = []

                for i in range(len(times)):
                    ylims.append((temp_y1, temp_y2))

        if type(cell_names[0]) == str:
            temp_name = cell_names[0]
            cell_names = []

            for i in range(len(times)):
                cell_names.append(temp_name)

        # Start loop
        results = dict()
        results['DateTime'] = []
        results['Cell'] = []
        flash_count = 0

        for i in range(len(times) - 1):
            print('Processing: {0} -- {1} UTC.'.format(times[i], times[i+1]))
            t_start = times[i]
            t_end = times[i+1]

            if t_start < storm.index.min():
                t_start = storm.index.min()
            if t_end > storm.index.max():
                t_end = storm.index.max()

            temp = storm.loc[t_start:t_end]

            for index, row in temp.iterrows():
                sources = storm_lma.get_sources_from_flash_number(
                                                           row['flash-number'])

                sources.sort_index(inplace=True)

                # Grab the first 20 sources. By looking at the initial sources
                # we can determine if the flash initiated in the cell of
                # interest and thus minimizing duplicates for large flashes
                # that span multiple cells. If the flash has less than 20
                # sources, then add a Nan to the result for that time.
                try:
                    flash = StormLMA(sources.iloc[0:20])
                    flash.convert_latlon_to_m(3, 4)

                    flash = flash.storm[flash.storm['x(m)'] > xlims[i][0]]
                    flash = flash[flash['x(m)'] < xlims[i][1]]
                    flash = flash[flash['y(m)'] > ylims[i][0]]
                    flash = flash[flash['y(m)'] < ylims[i][1]]

                    if len(flash) > min_sources:
                        flash_count += 1
                        results['DateTime'].append(index)
                        results['Cell'].append(cell_names[i])

                    else:
                        results['DateTime'].append(index)
                        results['Cell'].append(pd.np.nan)

                except IndexError:
                    results['DateTime'].append(index)
                    results['Cell'].append(pd.np.nan)

            print('  Flashes found: {0}'.format(flash_count))

        print('\nDone!')
        results = pd.Series(results['Cell'], index=results['DateTime'],
                            name='Cell')

        # Remove duplicate indices
        results = results.reset_index()
        results.sort_values(by='Cell', inplace=True)
        results.drop_duplicates(subset='index', inplace=True)
        results.set_index('index', inplace=True)
        results.sort_index(inplace=True)

        if inplace:
            self.storm.loc[:, 'Cell'] = results
        else:
            temp = self.storm.copy()
            temp.loc[:, 'Cell'] = results
            return temp


class Analysis(object):
    """
    A class structure to carry out the analysis of a storm system using
    LMA and .ods analyzed data.

        Parameters:
        ----------
        storm_lma: StormLMA
            StormLMA object of the storm of interest.
        storm_ods: StormODS
            StormODS object of the storm of interest.
        cells: dict (optional)
            Dictionary of Cell objects containing the information of
            each cell of the storm (if it has more than one or the user wishes
            to specify it for the one cell).

        Attributes:
        ----------
        storm_lma: StormLMA
            StormLMA object of the storm of interest.
        storm_ods: StormODS
            StormODS object of the storm of interest.
        cells: dict (optional)
            Dictionary of Cell objects containing the information of
            each cell of the storm (if it has more than one or the user wishes
            to specify it for the one cell).

    """

    def __init__(self, storm_lma, storm_ods, cells=None):
        """ Initialize the object. """

        self.lma = storm_lma
        self.ods = storm_ods
        self.cells = cells

    @staticmethod
    def nice_plots():
        """ Use the seaborn package to make figures nicer. """

        sns.set_context('talk', font_scale=2.0)

    def calculate_flash_areas(self):
        """
        Calculate the area of every flash in self.ods using the
        LMA sources from self.lma in plan view and using the convex hull
        approximation. Add the calculated area as a column on the
        self.ods DataFrame.

        """

        if 'x(m)' not in self.lma.storm.columns:
            self.lma.convert_latlon_to_m()

        # Select all sources with assigned charge
        temp_storm = self.lma.storm[self.lma.storm['charge'] != 0]

        unique = temp_storm['flash-number'].unique()
        indices = range(len(unique))

        area_65 = []
        area_61 = []
        area_75 = []
        area_71 = []
        area_mean = []
        date_time = []

        for index in indices:
            stations = 6
            chi = 5

            storm = StormLMA(self.lma.filtered_stations(stations, inplace=False))
            storm.filtered_chi_squared(chi, inplace=True)

            number = unique[index]
            # print(number, type(number))
            if np.isnan(number):
                area_65.append(np.nan)
                area_61.append(np.nan)
                area_75.append(np.nan)
                area_71.append(np.nan)
                continue

            flash = storm.get_sources_from_flash_number(number)
            flash = flash[flash['charge'] != 0]

            x = flash['x(m)'].get_values()
            y = flash['y(m)'].get_values()

            f = np.vstack((x, y)).T

            hull = scipy.spatial.ConvexHull(f)
            verts = f[hull.vertices].tolist()
            verts.append(f[hull.vertices[0]])
            lines = np.hstack([verts, np.roll(verts, -1, axis=0)])
            area_65.append(0.5 * abs(sum(x1 * y2 - x2 * y1 for
                                         x1, y1, x2, y2 in lines)))

            stations = 6
            chi = 1

            storm = StormLMA(self.lma.filtered_stations(stations, inplace=False))
            storm.filtered_chi_squared(chi, inplace=True)

            flash = storm.get_sources_from_flash_number(number)
            flash = flash[flash['charge'] != 0]

            x = flash['x(m)'].get_values()
            y = flash['y(m)'].get_values()

            f = np.vstack((x, y)).T

            hull = scipy.spatial.ConvexHull(f)
            verts = f[hull.vertices].tolist()
            verts.append(f[hull.vertices[0]])
            lines = np.hstack([verts, np.roll(verts, -1, axis=0)])
            area_61.append(0.5 * abs(sum(x1 * y2 - x2 * y1 for
                                         x1, y1, x2, y2 in lines)))

            # stations = 7
            # chi = 5
            #
            # storm = StormLMA(self.lma.filtered_stations(stations, inplace=False))
            # storm.filtered_chi_squared(chi, inplace=True)
            #
            # flash = storm.get_sources_from_flash_number(number)
            # flash = flash[flash['charge'] != 0]
            #
            # x = flash['x(m)'].get_values()
            # y = flash['y(m)'].get_values()
            #
            # f = np.vstack((x, y)).T
            #
            # hull = scipy.spatial.ConvexHull(f)
            # verts = f[hull.vertices].tolist()
            # verts.append(f[hull.vertices[0]])
            # lines = np.hstack([verts, np.roll(verts, -1, axis=0)])
            # area_75.append(0.5 * abs(sum(x1 * y2 - x2 * y1 for
            #                              x1, y1, x2, y2 in lines)))
            #
            # stations = 7
            # chi = 1
            #
            # storm = StormLMA(self.lma.filtered_stations(stations, inplace=False))
            # storm.filtered_chi_squared(chi, inplace=True)
            #
            # flash = storm.get_sources_from_flash_number(number)
            # flash = flash[flash['charge'] != 0]
            #
            # x = flash['x(m)'].get_values()
            # y = flash['y(m)'].get_values()
            #
            # f = np.vstack((x, y)).T
            #
            # hull = scipy.spatial.ConvexHull(f)
            # verts = f[hull.vertices].tolist()
            # verts.append(f[hull.vertices[0]])
            # lines = np.hstack([verts, np.roll(verts, -1, axis=0)])
            # area_71.append(0.5 * abs(sum(x1 * y2 - x2 * y1 for
            #                              x1, y1, x2, y2 in lines)))
            #
            # area_mean.append(np.mean([area_65[-1], area_61[-1],
            #                           area_71[-1], area_75[-1]]))
            date_time.append(flash.index[0])

        # Convert the areas from m^2 to km^2
        area_65 = np.array(area_65) * 1e-6
        area_61 = np.array(area_61) * 1e-6
        # area_75 = np.array(area_75) * 1e-6
        # area_71 = np.array(area_71) * 1e-6
        area_mean = np.array(area_mean) * 1e-6

        result = dict()
        result['flash-number'] = unique
        result['Area_65 (km^2)'] = area_65
        result['Area_61 (km^2)'] = area_61
        # result['Area_75 (km^2)'] = area_75
        # result['Area_71 (km^2)'] = area_71
        result['Area_mean (km^2)'] = area_mean
        # result['DateTime'] = date_time

        result = pd.DataFrame(result, index=date_time)

        return result

    def calculate_initiation_heights(self):
        """
        Calculate the initiation height of every flash in .ods file
        by averaging the first 10 LMA sources and appending the results
        to self.ods in a different column for comparison to the one done
        by me using the xlma software.
        """
        # Select all sources with assigned charge
        temp_storm = self.lma.storm[self.lma.storm['charge'] != 0]

        unique = temp_storm['flash-number'].unique()
        indices = range(len(unique))

        init_height = []
        date_time = []

        for index in indices:
            stations = 6
            chi = 1

            storm = StormLMA(self.lma.filtered_stations(stations, inplace=False))
            storm.filtered_chi_squared(chi, inplace=True)

            number = unique[index]

            if np.isnan(number):
                init_height.append(np.nan)
                continue

            flash = storm.get_sources_from_flash_number(number)
            if len(flash) == 0:
                continue
            # print(number, len(flash), flash['alt(m)'][:10].mean())
            init_height.append(flash['alt(m)'][:10].mean())
            date_time.append(flash.index[0])

        result = dict()
        result['InitiationHeightLMA(m)'] = init_height
        result = pd.DataFrame(result, index=date_time)

        return result

    def get_cell_initial_plotter(self, cell_name):
        """
        Return an LMAPlotter object with the data of the initial sources
        of all flashes in the cell.

        """
        return self.cells[cell_name].get_cell_initial_plotter()

    def get_cell_plotter(self, cell_name):
        """
        Return an LMAPlotter object with the data of all the sources
        of all flashes in the cell.

        """
        return self.cells[cell_name].get_cell_plotter()

    def get_type_sources(self, cell_name):
        """ Print the storm summary for each flash type in cell_name. """

        cell_ods = self.cells[cell_name].ods
        cell_lma = self.cells[cell_name].lma

        for t in cell_ods.storm['Type'].unique():
            s = 'Flash type: {0}'.format(t)
            print(s)
            print('-' * len(s))

            group = cell_ods.storm.groupby('Type').get_group(t)
            numbers = group['flash-number'].unique()

            sources = cell_lma.get_sources_from_flash_number(numbers)
            storm = StormLMA(sources)

            storm.print_storm_summary(charge='positive')
            storm.print_storm_summary(charge='negative')

    def plot_flash_areas(self, cell_name):
        """
        Plot a histogram of the flash areas of all the flash types
        in the cell, each in a separate figure.

        """

        self.cells[cell_name].plot_flash_areas()

    def plot_initiation_heights(self, cell_name):
        """
        Plot a histogram of the initiation height of all the flash types
        in the cell, each in a separate figure.

        """

        self.cells[cell_name].plot_initiation_heights()

    def plot_area_comparison(self, cell_name, flash_types=None):
        """
        Plot a superimposed histogram of the flash areas of the specified
        flash types in cell_name.

            Parameters
            ----------
            cell_name: str
                Name of the cell of interest.
            flash_types: list (optional)
                List of strings containing the flash types to plot. The
                default is to plot all flash types together.

            Returns
            -------
            ax: mpl Axes
                Matplotlib axes of the figure.

        """

        return self.cells[cell_name].plot_area_comparison(flash_types)

    def plot_initiation_height_comparison(self, cell_name, flash_types=None):
        """
        Plot a superimposed histogram of the initiation heights of the
        specified flash types in cell_name.

            Parameters
            ----------
            cell_name: str
                Name of the cell of interest.
            flash_types: list (optional)
                List of strings containing the flash types to plot. The
                default is to plot all flash types together.

            Returns
            -------
            ax: mpl Axes
                Matplotlib axes of the figure.

        """

        cell = self.cells[cell_name]
        return cell.plot_initiation_height_comparison(flash_types)

    def sort_into_cells(self, file_name, min_sources=5):
        """
        Sort all the flashes of the storm into the cells specified
        by self.cells

        Parameters:
        -----------
            file_name: str
                File name (without the file extension) to save the sorted
                data. The data will be saves in comma-separated values (.csv)
                and as a pickle (.p).
            min_sources: int (optional)
                    Minimum number of sources that would be considered a match

        """

        # Split the flashes into each cell
        results = []

        for cell in self.cells:
            temp = self.ods.sort_flashes_into_cells(self.lma,
                                                    self.cells[cell].times,
                                                    self.cells[cell].xlims,
                                                    self.cells[cell].ylims,
                                                    [self.cells[cell].name],
                                                    min_sources=min_sources,
                                                    inplace=False)
            results.append(temp)

        # Get the Series for each cell and reset their indices to aid in the
        # merge function
        dfs = []

        for result in results:
            data_frame = pd.DataFrame(result['Cell'])
            data_frame.reset_index(inplace=True)
            dfs.append(data_frame)

        # Merge teh cells together.
        temp = dfs[0]
        for i in range(len(dfs) - 1):
            temp = pd.merge(temp, dfs[i+1], how='outer')

        # Sort the entries by the cell names
        temp.sort_values(by='Cell', inplace=True)

        # Remove the duplicate times, set the index, and sort the data
        temp.drop_duplicates(subset='DateTime', inplace=True)
        temp.set_index('DateTime', inplace=True)
        temp.sort_index(inplace=True)

        # Merge all the Cell classifications into the self.ods DataFrame
        self.ods.storm.loc[:, 'Cell'] = temp

        # Save the data to make it easier to load next time
        file_csv = file_name + '.csv'
        self.ods.storm.to_csv(file_csv)

        file_p = file_name + '.p'
        self.ods.save_to_pickle(file_p)


class Cell(object):
    """
    A class structure to hold the data for a cell in a storm and basic
    functions.

        Parameters:
        -----------
        name: str
            Name of the cell.
        times: list
            List of datetime objects with the times each x,y limit is
            specified.
        xlims: list
            List of tuples containing the limits (in meters) in the x
            direction of a coordinate system centered at the ICLRT.
        ylims: list
            List of tuples containing the limits (in meters) in the y
            direction of a coordinate system centered at the ICLRT.

        Attributes:
        -----------
        name: str
            Name of the cell.
        times: list
            List of datetime objects with the times each x,y limit is
            specified.
        xlims: list
            List of tuples containing the limits (in meters) in the x
            direction of a coordinate system centered at the ICLRT.
        ylims: list
            List of tuples containing the limits (in meters) in the y
            direction of a coordinate system centered at the ICLRT.
        lma: StormLMA
            StormLMA object with the data for this cell.
        ods: StormODS
            StormODS object with the data for this cell.


    """

    def __init__(self, name, times, xlims, ylims):
        """ Initialize the object. """

        self.name = name
        self.times = times
        self.xlims = xlims
        self.ylims = ylims

    @staticmethod
    def _parse_ods_file(file):
        """ Parse the .ods files to generate the DataFrame. """

        cell = pd.read_csv(file)

        # Combine the date and time columns into a single datetime column
        cell.insert(1, 't_start',
                    ['{0} {1}'.format(cell['Date'][i], cell['t1'][i])
                     for i in
                     range(len(cell))])
        cell['t_start'] = pd.to_datetime(cell['t_start'],
                                         format='%Y-%m-%d %H:%M')

        cell.insert(2, 't_end',
                    ['{0} {1}'.format(cell['Date'][i], cell['t2'][i])
                     for i in
                     range(len(cell))])
        cell['t_end'] = pd.to_datetime(cell['t_end'],
                                       format='%Y-%m-%d %H:%M')

        return cell

    def get_cell_initial_plotter(self):
        """
        Return an LMAPlotter object with the data of the initial sources
        of all flashes in the cell.

        """

        numbers = self.lma.storm['flash-number'].unique()

        return self.lma.get_initial_plotter_from_number(numbers)

    def get_cell_plotter(self):
        """
        Return an LMAPlotter object with the data of all the sources
        of all flashes in the cell.

        """

        numbers = self.lma.storm['flash-number'].unique()

        return self.lma.get_flash_plotter_from_number(numbers)

    @classmethod
    def from_ods_file(cls, file):
        """ Initialize the object from files and dates """

        data = cls._parse_ods_file(file)
        grouped = data.groupby('Cell')

        cells = []

        for index in grouped.groups.keys():
            name = [str(index)]

            times = []
            for i in grouped.groups[index]:
                start = data['t_start'][i].to_datetime()
                end = data['t_end'][i].to_datetime()
                times.append(tuple([start, end]))

            x1 = data['x1'][grouped.groups[index]]
            x2 = data['x2'][grouped.groups[index]]
            y1 = data['y1'][grouped.groups[index]]
            y2 = data['y2'][grouped.groups[index]]

            xlims = [(x1[i], x2[i]) for i in x1.index]
            ylims = [(y1[i], y2[i]) for i in y1.index]

            # Convert limits to meters
            xlims = np.array(xlims) * 1e3
            ylims = np.array(ylims) * 1e3

            cells.append(cls(name, times, xlims, ylims))

        return cells

    def plot_flash_areas(self):
        """
        Plot a histogram of the flash areas of all the flash types
        in the cell, each in a separate figure.

        """

        for t in self.ods.storm['Type'].unique():
            self.ods.analyze_flash_areas(flash_type=t)

    def plot_initiation_heights(self):
        """
        Plot a histogram of the initiation height of all the flash types
        in the cell, each in a separate figure.

        """

        for t in self.ods.storm['Type'].unique():
            self.ods.analyze_initiation_heights(flash_type=t)

    def plot_area_comparison(self, flash_types=None):
        """
        Plot a superimposed histogram of the flash areas of the specified
        flash types in the cell.

            Parameters
            ----------
            flash_types: list (optional)
                List of strings containing the flash types to plot. The
                default is to plot all flash types together.

            Returns
            -------
            ax: mpl Axes
                Matplotlib axes of the figure.

        """

        if flash_types is None:
            flash_types = self.ods.storm['Type'].unique()

        types = []
        for t in flash_types:
            types.append(self.ods.get_flash_type(t))

        series = []
        for t in types:
            series.append(t['Area (km^2)'])

        series_dict = dict()
        for i in range(len(types)):
            if flash_types[i] == 'IC':
                key = ' IC'
            else:
                key = flash_types[i]

            series_dict[key] = series[i]

        data_frame = pd.DataFrame(series_dict)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        data_frame.plot.hist(alpha=0.5, ax=ax)

        title = 'Histogram of Flash Areas (from Plan View)'
        ax.set_title(title)
        ax.set_xlabel(r'Flash Area (km$^2$)')
        ax.legend()

        return ax

    def plot_initiation_height_comparison(self, flash_types=None):
        """
        Plot a superimposed histogram of the initiation heights of the
        specified flash types in the cell.

            Parameters
            ----------
            flash_types: list (optional)
                List of strings containing the flash types to plot. The
                default is to plot all flash types together.

            Returns
            -------
            ax: mpl Axes
                Matplotlib axes of the figure.

        """

        if flash_types is None:
            flash_types = self.ods.storm['Type'].unique()

        types = []
        for t in flash_types:
            types.append(self.ods.get_flash_type(t))

        series = []
        for t in types:
            series.append(t['Initiation Height (km)'])

        series_dict = dict()
        for i in range(len(types)):
            if flash_types[i] == 'IC':
                key = ' IC'
            else:
                key = flash_types[i]

            series_dict[key] = series[i]

        data_frame = pd.DataFrame(series_dict)

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        data_frame.plot.hist(alpha=0.5, ax=ax)

        title = 'Histogram of Initiation Heights'
        ax.set_title(title)
        ax.set_xlabel('Initiation Height (km)')
        ax.legend()

        return ax

    def set_lma(self, lma):
        self.lma = lma

    def set_ods(self, ods):
        self.ods = ods


class PostXLMAAnalysis(object):
    """
    A class structure to perform a similar analysis done when generating
    the .ods files. The functions in this class will allows the user
    to extract the same information in the .ods files but using the actual
    LMA data for improved accuracy.

    Parameters:
    -----------
        storm_lma: StormLMA object
            Data exported from the xlma software after doing charge analysis.

    Attributes:
    -----------
        lma: StormLMA object
            Data to be processed.
        processed_data: Pandas DataFrame
            Container for the processed data.

    """

    def __init__(self, storm_lma):
        """ Initialize the object. """

        self.lma = storm_lma
        self.processed_data = None

        self.lma.convert_latlon_to_m(verbose=True)

    def set_flash_types(self):
        numbers = self.lma.storm['flash-number'].unique()

        for number in numbers:
            flash = StormLMA(self.lma.get_sources_from_flash_number(number))
            if len(flash.storm) < 75:
                continue

            fig_plan = plt.figure()
            ax_plan = fig_plan.add_subplot(211)

            fig_alt_t = plt.figure()
            ax_alt_t = fig_alt_t.add_subplot(212)
            
            # Plot graphs
            p = flash.get_flash_plotter_from_number(number)
            p.set_coloring('charge')
            p.plot_plan(ax=ax_plan)
            p.plot_alt_t(ax=ax_alt_t)
            plt.show()

            # Get all limits from both plots
            xlims = p.ax_plan.get_xlim()
            ylims = p.ax_plan.get_ylim()
            tlims = p.ax_alt_t.get_xlim()
            zlims = np.array(p.ax_alt_t.get_ylim())*1e3
            
            # Filter sources in flash
            filtered = flash.storm[flash.storm['x(m)'] >= xlims[0]]
            filtered = filtered[filtered['x(m)'] <= xlims[-1]]
            filtered = filtered[filtered['y(m)'] >= ylims[0]]
            filtered = filtered[filtered['y(m)'] <= ylims[-1]]
            filtered = filtered[filtered['alt(m)'] >= zlims[0]]
            filtered = filtered[filtered['alt(m)'] <= zlims[-1]]

            t1 = datetime.datetime.strftime(mpl.dates.num2date(tlims[0]),
                                            '%Y-%m-%d %H:%M:%S.%f')
            t2 = datetime.datetime.strftime(mpl.dates.num2date(tlims[-1]),
                                            '%Y-%m-%d %H:%M:%S.%f')
            filtered = filtered.loc[t1:t2]

            flash = StormLMA(filtered)

            print(flash.storm)







