#!/usr/bin/env python

# Add personal packages directory to path
import datetime
import numpy as np

# Import custom module
import iclrt_tools.lat_lon.lat_lon as latlon


class LMAFile(object):
    def __init__(self, file_name, load_data=True, shift=(0, 0)):
        self.file_name = file_name
        self.shift = shift

        # Initialize all variables
        self.date = None
        self.center_coordinate = None
        self.num_stations = None
        self.num_active_stations = None
        self.active_stations = None
        self.min_stations_per_solution = None
        self.max_rc2 = None
        self.max_rc2 = None
        self.station_mask_order = None
        self.data_format = None
        self.num_events = None

        self.stations_info = None
        self.stations_data = None

        self.data = None
        self.data_loaded = False

        self.load_file(load_data)

    def load_file(self, load_data=True):
        with open(self.file_name) as f:
            self.stations_info = []
            self.stations_data = []

            for line in f:
                if 'Analysis program:' in line:
                    self.program = line.split(":")[-1].strip()

                elif 'Data start time' in line:
                    date = line.split(':')[1].split()[0]
                    self.date = datetime.datetime.strptime(date, '%m/%d/%y')

                elif 'Coordinate center (lat,lon,alt):' in line:
                    values = line.split(":")[1].split()
                    self.center_coordinate = latlon.Location(values[0],
                                                                values[1],
                                                                values[2])

                elif 'Number of stations:' in line:
                    self.num_stations = int(line.split(":")[1])

                elif 'Number of active stations:' in line:
                    self.num_active_stations = int(line.split(":")[1])

                elif 'Active stations:' in line:
                    self.active_stations = line.split(":")[1].strip()

                elif 'Minimum number of stations per solution:' in line:
                    self.min_stations_per_solution = int(line.split(":")[1])

                elif 'Maximum reduced chi-squared:' in line:
                    self.max_rc2 = float(line.split(":")[1])

                elif 'Sta_info:' in line:
                    self.stations_info.append(line.split(":")[1])

                elif 'Sta_data' in line:
                    self.stations_data.append(line.split(":")[1])

                elif 'Station mask order:' in line:
                    self.station_mask_order = line.split(":")[1]

                elif 'Data format:' in line:
                    self.data_format = line.split(":")[1]

                elif 'Number of events:' in line:
                    self.num_events = int(line.split(":")[1])

            if load_data:
                self.load_data()

    def load_data(self):
        with open(self.file_name) as f:
            self.data = []
            flag = False

            for line in f:
                if '*** data ***' in line:
                    flag = True
                    continue

                if flag:
                    words = line.split()

                    source = LMASource(self.date, words[0], words[1], words[2],
                                       words[3], words[4], words[5], words[6])

                    source.set_xyz_coords(self.center_coordinate, self.shift)
                    self.data.append(source)

        self.data_loaded = True


class XLMAExportedFile(LMAFile):
    def __init__(self, file_name, load_data=True, shift=(0, 0)):
        super(XLMAExportedFile, self).__init__(file_name, False, shift)

        self.file_name = file_name
        self.center_coordinate = latlon.Location(29.9429917, -82.0332305, 0.00)

        if load_data:
            self.load_data()

    def load_data(self):
        with open(self.file_name) as f:
            self.data = []
            flag = False

            for line in f:
                if '*** data ***' in line:
                    flag = True
                    continue

                if flag:
                    words = line.split()

                    source = LMASource(self.date, words[0], words[1], words[2],
                                       words[3], words[4], words[6], words[9], words[8])

                    source.set_xyz_coords(self.center_coordinate, self.shift)
                    self.data.append(source)

        self.data_loaded = True


class LMASource(object):
    def __init__(self, date, seconds_of_day, lat, lon, alt, rc2,
                 power, mask, charge=0):
        if isinstance(date, datetime.datetime):
            self.date = date
        else:
            # date must be in format MM/DD/YY
            self.date = datetime.datetime.strptime(date, '%m/%d/%y')

        dt = datetime.timedelta(seconds=float(seconds_of_day))
        self.time = self.date + dt
        self.seconds_of_day = float(seconds_of_day)

        self.location = latlon.Location(float(lat), float(lon), float(alt))
        self.rc2 = float(rc2)
        self.power = float(power)
        self.mask = '{0:08d}'.format(int(bin(int(mask, 16))[2:]))
        self.charge = int(charge)
        self.num_stations = self.mask.count('1')
        self.xyz_coords = None

    def set_xyz_coords(self, center, shift=(0, 0)):
        """
        :param center: Location object for center
        :return: relative x,y,z of the source with relation to center
        """

        # Convert to WGS-84
        xyz = self.location.xyz_transform()
        center_xyz = center.xyz_transform()

        # Center around "center"
        x = xyz[0] - center_xyz[0]
        y = xyz[1] - center_xyz[1]
        z = xyz[2] - center_xyz[2]

        # Apply rotations to correct orientations
        # This was ported from the xlma IDL code from file lonlat_to_xy.pro

        lonr = -center.lonr
        colat = -(np.pi/2 - center.latr)

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

        self.xyz_coords = x + shift[0], y + shift[1], z

    def __repr__(self):
        if self.charge < 0:
            charge = "Negative"
        elif self.charge > 0:
            charge = "Positive"
        else:
            charge = "Undetermined"

        s = ""
        s += "Date: {0}".format(self.date.strftime('%m/%d/%y'))
        s += "Time: {0}".format(self.time.strftime('%H:%M:%S.%f'))
        s += "Location (lat, lon, alt): {lat}, {lon}, {alt}".format(
                                lat=self.location.lat,
                                lon=self.location.lon,
                                alt=self.location.alt)
        s += "Power (dBW): {0}".format(self.power)
        s += "Reduced Chi^2: {0}".format(self.rc2)
        s += "Number of stations used in solution: {0}".format(
                                self.num_stations)
        s += "Station Mask: {0}".format(self.mask)
        s += "Charge: {0}".format(charge)

        return s
